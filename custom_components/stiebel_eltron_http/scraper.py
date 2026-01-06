"""Stiebel Eltron ISG scraping client."""

from __future__ import annotations

import json
import re
import socket
from typing import Any

import aiohttp
import async_timeout
import bs4
from homeassistant.const import ATTR_SW_VERSION

from .const import (
    DIAGNOSIS_SYSTEM_PATH,
    EXPECTED_HTML_TITLE,
    HTTP_CONNECTION_TIMEOUT,
    INFO_HEATPUMP_PATH,
    INFO_SYSTEM_PATH,
    LOGGER,
    MAC_ADDRESS_KEY,
    START_OPERATION_MODE_KEY,
    START_PORTAL_OK,
    START_SYSTEM_OK,
    START_SG_READY_ACTIVE,
    START_SG_READY_STATE,
    START_ENERGY_MGMT_OK,
    OUTSIDE_TEMPERATURE_KEY,
    PROFILE_NETWORK_PATH,
    ROOM_HUMIDITY_KEY,
    ROOM_TEMPERATURE_KEY,
    DHW_TEMPERATURE_KEY,
    DHW_SET_TEMPERATURE_KEY,
    TOTAL_HEAT_PRODUCED_KEY,
    HEAT_PRODUCED_TODAY_KEY,
    TOTAL_DHW_PRODUCED_KEY,
    DHW_PRODUCED_TODAY_KEY,
    TOTAL_HEATING_CONSUMED_KEY,
    HEATING_CONSUMED_TODAY_KEY,
    TOTAL_DHW_CONSUMED_KEY,
    DHW_CONSUMED_TODAY_KEY,
    RETURN_TEMPERATURE_KEY,
    SUPPLY_TEMPERATURE_KEY,
    FROST_PROTECTION_TEMPERATURE_KEY,
    COMPRESSOR_INLET_TEMPERATURE_KEY,
    HOT_GAS_TEMPERATURE_KEY,
    CONDENSER_TEMPERATURE_KEY,
    OIL_SUMP_TEMPERATURE_KEY,
    LOW_PRESSURE_KEY,
    HIGH_PRESSURE_KEY,
    WATER_FLOW_KEY,
    INVERTER_CURRENT_KEY,
    INVERTER_VOLTAGE_KEY,
    COMPRESSOR_SPEED_ACTUAL_KEY,
    COMPRESSOR_SPEED_TARGET_KEY,
    FAN_POWER_RELATIVE_KEY,
    EVAPORATOR_INLET_TEMPERATURE_KEY,
    EVAPORATOR_OUTLET_TEMPERATURE_KEY,
    INVERTER_POWER_INPUT_KEY,
    INVERTER_POWER_KEY,
    EFFICIENCY_HEATING_TODAY_KEY,
    EFFICIENCY_HEATING_1_12M_KEY,
    EFFICIENCY_HEATING_13_24M_KEY,
    EFFICIENCY_DHW_TODAY_KEY,
    EFFICIENCY_DHW_1_12M_KEY,
    EFFICIENCY_DHW_13_24M_KEY,
    ACTUAL_TEMPERATURE_HK_1_KEY,
    SET_TEMPERATURE_HK_1_KEY,
    ACTUAL_TEMPERATURE_HK_2_KEY,
    SET_TEMPERATURE_HK_2_KEY,
    ACTUAL_BUFFER_TEMPERATURE_KEY,
    SET_BUFFER_TEMPERATURE_KEY,
    DUAL_MODE_TEMP_HZG_KEY,
    DUAL_MODE_TEMP_WW_KEY,
    RUNTIME_VD_HEATING_KEY,
    RUNTIME_VD_DHW_KEY,
    RUNTIME_VD_DEFROST_KEY,
    DEFROST_TIME_KEY,
    DEFROST_STARTS_KEY,
    COMPRESSOR_STARTS_KEY,
    DEFAULT_LANGUAGE,
    DEFAULT_FETCH_ENERGY,
    WCCI_ENDPOINT,
    WCCI_INPUT_MODE_KEY,
    WCCI_INPUT_SOURCE_KEY,
    WCCI_BUFFER_KEY,
    WCCI_OPERATING_MODE_KEY,
    WCCI_USER_POWER_LIMIT_KEY,
    WCCI_LOAD_TEMP_ROOM_1_KEY,
    WCCI_LOAD_TEMP_ROOM_2_KEY,
    WCCI_LOAD_TEMP_ROOM_3_KEY,
    WCCI_LOAD_TEMP_ROOM_4_KEY,
    WCCI_LOAD_TEMP_ROOM_5_KEY,
    WCCI_LOAD_TEMP_BUFFER_KEY,
    WCCI_LOAD_TEMP_DHW_KEY,
    WCCI_LIMIT_FUNCTIONALITY_BLOCKED_KEY,
)

from . import parsing
from .i18n import CanonicalKey, to_canonical_key, get_aliases
from .mapping import CANONICAL_TO_CONST, ENERGY_CONSUMED_MAP

# Reference the centralized alias map (now in parsing.py).
HEADER_ALIASES = parsing.HEADER_ALIASES


class StiebelEltronScrapingClientError(Exception):
    """Exception to indicate a general scraping error."""

    def __init__(self, message: str) -> None:
        """Initialize with an explanation message."""
        super().__init__(message)


class StiebelEltronScrapingClientCommunicationError(
    StiebelEltronScrapingClientError,
):
    """Exception to indicate a communication error."""


class StiebelEltronScrapingClientAuthenticationError(
    StiebelEltronScrapingClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise StiebelEltronScrapingClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


class StiebelEltronScrapingClient:
    """Scrape data from the Stiebel Eltron ISG web portal."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        language: str = DEFAULT_LANGUAGE,
        fetch_energy: bool = DEFAULT_FETCH_ENERGY,
    ) -> None:
        """Stiebel Eltron scraping client.

        language: controls which localized header aliases are tried when parsing.
        """
        self._host = host
        self._session = session
        self._language = language or DEFAULT_LANGUAGE
        # Whether to attempt fetching the Energy page /?s=1,8 during full fetch
        self._fetch_energy = bool(fetch_energy)

    async def async_test_connect(self) -> Any:
        """Test that we can connect."""
        url = f"http://{self._host}/"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            self._check_title(response)
            # Attempt to auto-detect page language and store it on the client.
            try:
                detected = self._auto_detect_language(response)
                self._language = detected
                LOGGER.debug("Auto-detected ISG language: %s", self._language)
            except Exception:  # keep detection best-effort
                LOGGER.debug("Language auto-detection failed; keeping default: %s", self._language)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return response

    def _auto_detect_language(self, response: str) -> str:
        """Try to detect the ISG page language from the language-switch element.

        This is a simple heuristic that searches for the language indicator in
        the UI. Returns a language code for one of 12 supported languages:
        en, de, fr, nl, it, sv, es, pl, cs, hu, fi, da (defaults to 'en' when unsure).
        """
        # Only use the language-switch element on the page to detect language.
        # Some hosts use meta tags influenced by the local machine which are
        # unreliable for determining the ISG UI language. The ISG pages include
        # a language switch element like:
        # <div class="eingestelle_sprache"><strong><a href="?s=5,3">ENGLISH</a></strong></div>
        # The scraper interprets the visible link text as the current UI language.
        # Supported link text values (case-insensitive):
        #   'ENGLISH' -> en | 'DEUTSCH'/'GERMAN' -> de | 'FRANÇAIS'/'FRANCAIS'/'FRENCH' -> fr
        #   'NEDERLANDS'/'DUTCH' -> nl | 'ITALIANO'/'ITALIAN' -> it | 'SVENSKA'/'SWEDISH' -> sv
        #   'ESPAÑOL'/'ESPANOL'/'SPANISH' -> es | 'POLSKI'/'POLISH' -> pl
        #   'ČEŠTINA'/'CESTINA'/'CZECH' -> cs | 'MAGYAR'/'HUNGARIAN' -> hu
        #   'SUOMI'/'FINNISH' -> fi | 'DANSK'/'DANISH' -> da
        if not isinstance(response, str):
            return DEFAULT_LANGUAGE

        try:
            soup = bs4.BeautifulSoup(response, "html.parser")
            lang_elem = soup.select_one(".eingestelle_sprache a")
            if lang_elem and lang_elem.string:
                link_text = lang_elem.string.strip().lower()
                # Interpret the visible link text as the current UI language.
                if "english" in link_text:
                    return "en"
                if "deutsch" in link_text or "german" in link_text:
                    return "de"
                if "français" in link_text or "francais" in link_text or "french" in link_text:
                    return "fr"
                if "nederlands" in link_text or "dutch" in link_text:
                    return "nl"
                if "italiano" in link_text or "italian" in link_text:
                    return "it"
                if "svenska" in link_text or "swedish" in link_text:
                    return "sv"
                if "español" in link_text or "espanol" in link_text or "spanish" in link_text:
                    return "es"
                if "polski" in link_text or "polish" in link_text:
                    return "pl"
                if "čeština" in link_text or "cestina" in link_text or "czech" in link_text:
                    return "cs"
                if "magyar" in link_text or "hungarian" in link_text:
                    return "hu"
                if "suomi" in link_text or "finnish" in link_text:
                    return "fi"
                if "dansk" in link_text or "danish" in link_text:
                    return "da"
        except Exception:
            # Best-effort; fall back to default language
            pass

        return DEFAULT_LANGUAGE

    async def async_get_device_info(self) -> Any:
        """Retrieve device info from the ISG device."""
        result = {}

        result.update(await self.async_get_mac_address())
        result.update(await self.async_get_versions())

        return result

    async def async_get_mac_address(self) -> Any:
        """Retrieve the MAC address from the ISG device."""
        return await self.async_scrape_profile_network()

    async def async_get_versions(self) -> Any:
        """Retrieve the hardware and software versions from the ISG device."""
        return await self.async_scrape_diagnosis_system()

    async def async_fetch_all(self) -> Any:
        """Scrape all available data from the ISG web portal."""
        result = {}

        # Also attempt to fetch the START page which contains overview info
        # such as Betriebsart, Systemstatus and Portalstatus.
        try:
            start_page = await self.async_scrape_start()
            result.update(start_page)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError):
            LOGGER.debug("Start page (s=0) not available or failed to parse")

        info_system_result = await self.async_scrape_info_system()
        result.update(info_system_result)

        info_system_heatpump = await self.async_scrape_info_heatpump()
        result.update(info_system_heatpump)

        # Optionally attempt to fetch the Energy / Energiebilanz page which some
        # devices expose at /?s=1,8. This can be controlled via the client
        # `fetch_energy` flag (stored in self._fetch_energy). When enabled we
        # reuse the heatpump extractor to parse totals, consumption and
        # efficiency tables that appear on s=1,8 pages.
        if self._fetch_energy:
            try:
                info_system_energy = await self.async_scrape_info_energy()
                result.update(info_system_energy)
            except (aiohttp.ClientError, StiebelEltronScrapingClientError):
                # Keep best-effort: do not make the whole fetch fail if /?s=1,8
                # is missing or not accessible on this device.
                LOGGER.debug("Info Energy page (s=1,8) not available or failed to parse")
        else:
            LOGGER.debug("Skipping Energy page (s=1,8) because fetch_energy is disabled for this client")

        info_system_diagnosis = await self.async_scrape_diagnosis_system()
        result.update(info_system_diagnosis)

        # Optionally attempt to fetch WCCI (Power Influence) configuration
        # from /?s=4,25 endpoint. This returns JSON data with WCCI settings.
        try:
            wcci_data = await self.async_scrape_wcci()
            result.update(wcci_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            # Keep best-effort: do not make the whole fetch fail if WCCI
            # is not available or not configured on this device.
            LOGGER.debug("WCCI data not available or failed to parse")

        # Optionally attempt to fetch heating configuration pages
        # These provide read-only configuration values for heating circuits
        try:
            hc1_data = await self.async_scrape_heating_hc1()
            result.update(hc1_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("Heating Circuit 1 config page not available or failed to parse")

        try:
            hc2_data = await self.async_scrape_heating_hc2()
            result.update(hc2_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("Heating Circuit 2 config page not available or failed to parse")

        try:
            basic_data = await self.async_scrape_heating_basic()
            result.update(basic_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("Heating basic settings page not available or failed to parse")

        try:
            summer_data = await self.async_scrape_heating_summer()
            result.update(summer_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("Heating summer mode page not available or failed to parse")

        try:
            pump_cycles_data = await self.async_scrape_heating_pump_cycles()
            result.update(pump_cycles_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("Heating pump cycles page not available or failed to parse")

        try:
            external_data = await self.async_scrape_heating_external()
            result.update(external_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("Heating external heat source page not available or failed to parse")

        try:
            dhw_temps_data = await self.async_scrape_dhw_temperatures()
            result.update(dhw_temps_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW temperatures page not available or failed to parse")

        try:
            dhw_standard_data = await self.async_scrape_dhw_standard()
            result.update(dhw_standard_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW standard settings page not available or failed to parse")

        try:
            dhw_learning_data = await self.async_scrape_dhw_learning()
            result.update(dhw_learning_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW learning function page not available or failed to parse")

        try:
            dhw_combi_data = await self.async_scrape_dhw_combi_cylinder()
            result.update(dhw_combi_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW combi cylinder page not available or failed to parse")

        try:
            dhw_output_data = await self.async_scrape_dhw_output()
            result.update(dhw_output_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW output page not available or failed to parse")

        try:
            dhw_max_flow_data = await self.async_scrape_dhw_max_flow_temp()
            result.update(dhw_max_flow_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW max flow temp page not available or failed to parse")

        try:
            dhw_pasteur_data = await self.async_scrape_dhw_pasteurisation()
            result.update(dhw_pasteur_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW pasteurisation page not available or failed to parse")

        try:
            dhw_external_data = await self.async_scrape_dhw_external()
            result.update(dhw_external_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("DHW external heat source page not available or failed to parse")

        try:
            sg_ready_data = await self.async_scrape_sg_ready()
            result.update(sg_ready_data)
        except (aiohttp.ClientError, StiebelEltronScrapingClientError, ValueError):
            LOGGER.debug("SG Ready page not available or failed to parse")

        LOGGER.debug("Scraped data: %s", result)
        return result

    async def async_scrape_info_system(self) -> Any:
        """Scrape data from the Info / System page."""
        url = f"http://{self._host}{INFO_SYSTEM_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_info_system(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_info_heatpump(self) -> Any:
        """Scrape data from the Info / Heat Pump page."""
        url = f"http://{self._host}{INFO_HEATPUMP_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_info_heatpump(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_info_energy(self) -> Any:
        """Scrape data from the Info / Energy (Energiebilanz) page (s=1,8).

        The 'Energy' page contains the same tables (amount of heat / power
        consumption) as some heat-pump screenshots. Reuse the heatpump extractor
        logic so we parse totals and consumption values consistently.
        """
        from .const import INFO_ENERGY_PATH

        url = f"http://{self._host}{INFO_ENERGY_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            # Reuse the heatpump page extractor: it knows how to extract AMOUNT
            # OF HEAT and POWER CONSUMPTION tables which appear on s=1,8 pages.
            result = self._extract_info_energy(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_diagnosis_system(self) -> Any:
        """Scrape data from the Diagnosis / System page."""
        url = f"http://{self._host}{DIAGNOSIS_SYSTEM_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_diagnosis_system(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_profile_network(self) -> Any:
        """Scrape data from the Profile / Network page."""
        url = f"http://{self._host}{PROFILE_NETWORK_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_profile_network(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_start(self) -> Any:
        """Scrape data from the Start page (s=0)."""
        url = f"http://{self._host}/?s=0"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_start_page(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_wcci(self) -> Any:
        """Scrape WCCI (Power Influence) configuration data.
        
        This fetches JSON data from the WCCI endpoint which provides:
        - Input mode (OFF, SG READY, POWER LIMITATION modes)
        - Input source (MODBUS, KNX, WPM, ISG)
        - Buffer configuration
        - Operating mode
        - User power limit
        - Load temperatures for heating circuits and DHW
        
        Returns a dict with WCCI sensor keys.
        """
        # First get session token from the WCCI page
        from .const import WCCI_PATH
        page_url = f"http://{self._host}{WCCI_PATH}"
        
        try:
            page_response = await self._api_wrapper(
                method="GET",
                url=page_url,
            )
            # Extract session token from page HTML
            soup = bs4.BeautifulSoup(page_response, "html.parser")
            token_div = soup.find("div", {"class": "sessionToken", "id": "sessionToken"})
            if not token_div:
                LOGGER.warning("WCCI: Could not find session token in page")
                return {}
            
            session_token = token_div.get_text(strip=True)
            LOGGER.debug("WCCI: Found session token: %s", session_token)
            
            # Now fetch the JSON endpoint data
            endpoint_url = f"http://{self._host}{WCCI_ENDPOINT}?sessionToken={session_token}"
            json_response = await self._api_wrapper(
                method="GET",
                url=endpoint_url,
            )
            
            # Parse JSON response
            data = json.loads(json_response)
            LOGGER.debug("WCCI: Received data: %s", data)
            
            result = self._extract_wcci_data(data)
            
        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to WCCI endpoint - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        except json.JSONDecodeError as exception:
            msg = f"Failed to parse WCCI JSON response - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    def _extract_wcci_data(self, data: dict) -> dict:
        """Extract WCCI configuration values from JSON response.
        
        The WCCI endpoint returns data with scaled values:
        - Temperatures are in tenths of degrees (230 = 23.0°C)
        - Power limit is in hundredths of kW (420 = 4.20 kW)
        - Enum values are strings or integers
        
        Args:
            data: JSON response dict from WCCI endpoint
            
        Returns:
            dict: Extracted sensor values with proper scaling
        """
        result: dict[str, object] = {}
        
        # Input mode (string: "OFF", "SGREADY", "POWERLIMITMODE", etc.)
        if "inputMode" in data:
            result[WCCI_INPUT_MODE_KEY] = str(data["inputMode"])
        
        # Input source (string: "MODBUS", "KNX", "WPM", "ISG")
        if "inputSource" in data:
            result[WCCI_INPUT_SOURCE_KEY] = str(data["inputSource"])
        
        # Buffer configuration (string: "NOBUFFER", "BUFFER_WITHOUT_MIXER", etc.)
        if "buffer" in data:
            result[WCCI_BUFFER_KEY] = str(data["buffer"])
        
        # Operating mode (string: "NO_LIMITATION", etc.)
        if "operatingMode" in data:
            result[WCCI_OPERATING_MODE_KEY] = str(data["operatingMode"])
        
        # Limit functionality blocked (boolean)
        if "limitFunctionalityBlocked" in data:
            result[WCCI_LIMIT_FUNCTIONALITY_BLOCKED_KEY] = bool(data["limitFunctionalityBlocked"])
        
        # User power limit (scaled by 100, convert to kW)
        if "userPowerLimit" in data:
            raw_value = data["userPowerLimit"]
            result[WCCI_USER_POWER_LIMIT_KEY] = float(raw_value) / 100.0
        
        # Load temperatures (scaled by 10, convert to °C)
        temp_fields = [
            ("loadTempRoom_1", WCCI_LOAD_TEMP_ROOM_1_KEY),
            ("loadTempRoom_2", WCCI_LOAD_TEMP_ROOM_2_KEY),
            ("loadTempRoom_3", WCCI_LOAD_TEMP_ROOM_3_KEY),
            ("loadTempRoom_4", WCCI_LOAD_TEMP_ROOM_4_KEY),
            ("loadTempRoom_5", WCCI_LOAD_TEMP_ROOM_5_KEY),
            ("loadTempBuffer", WCCI_LOAD_TEMP_BUFFER_KEY),
            ("loadTempDhw", WCCI_LOAD_TEMP_DHW_KEY),
        ]
        
        for json_key, const_key in temp_fields:
            if json_key in data:
                raw_value = data[json_key]
                result[const_key] = float(raw_value) / 10.0
        
        LOGGER.debug("Extracted WCCI data: %s", result)
        return result

    async def async_scrape_heating_hc1(self) -> Any:
        """Scrape Heating Circuit 1 configuration data.
        
        This fetches configuration values from the Heating Circuit 1 page (s=4,2,0):
        - Comfort temperature
        - Eco temperature
        - Minimum temperature (optional)
        - Heating curve rise
        
        Returns a dict with HC1 sensor keys.
        """
        from .const import HEATING_HC1_PATH
        return await self._scrape_heating_config_page(HEATING_HC1_PATH, "HC1")

    async def async_scrape_heating_hc2(self) -> Any:
        """Scrape Heating Circuit 2 configuration data.
        
        This fetches configuration values from the Heating Circuit 2 page (s=4,2,1):
        - Comfort temperature
        - Eco temperature
        - Minimum temperature (optional)
        - Maximum temperature
        - Mixer dynamics
        - Heating curve rise
        
        Returns a dict with HC2 sensor keys.
        """
        from .const import HEATING_HC2_PATH
        return await self._scrape_heating_config_page(HEATING_HC2_PATH, "HC2")

    async def async_scrape_heating_basic(self) -> Any:
        """Scrape Heating Basic Settings configuration data.
        
        This fetches configuration values from the Basic Settings page (s=4,2,2):
        - Buffer operation
        - Maximum return temperature
        - Maximum flow temperature
        - Fixed value operation (optional)
        - Frost protection temperature
        
        Returns a dict with basic heating sensor keys.
        """
        from .const import HEATING_BASIC_PATH
        return await self._scrape_heating_config_page(HEATING_BASIC_PATH, "BASIC")

    async def async_scrape_heating_summer(self) -> Any:
        """Scrape Heating Summer Mode configuration data.
        
        This fetches configuration values from the Summer Mode page (s=4,2,3):
        - Summer mode (ON/OFF)
        - Outside temperature threshold
        - Building heat buffer
        
        Returns a dict with summer mode sensor keys.
        """
        from .const import HEATING_SUMMER_PATH
        return await self._scrape_heating_config_page(HEATING_SUMMER_PATH, "SUMMER")

    async def async_scrape_heating_pump_cycles(self) -> Any:
        """Scrape Heating Pump Cycles configuration data.
        
        This fetches configuration values from the Pump Cycles page (s=4,2,4):
        - Pump cycles (ON/OFF)
        
        Returns a dict with pump cycles sensor key.
        """
        from .const import HEATING_PUMP_CYCLES_PATH
        return await self._scrape_heating_config_page(HEATING_PUMP_CYCLES_PATH, "PUMP_CYCLES")

    async def async_scrape_heating_external(self) -> Any:
        """Scrape Heating External Heat Source configuration data.
        
        This fetches configuration values from the External Heat Source page (s=4,2,5):
        - External heat source type
        - Heating curve gap
        - Blocking time EVU
        - Dual mode temperature
        - Lower application limit (optional)
        
        Returns a dict with external heat source sensor keys.
        """
        from .const import HEATING_EXTERNAL_PATH
        return await self._scrape_heating_config_page(HEATING_EXTERNAL_PATH, "EXTERNAL")

    async def async_scrape_dhw_temperatures(self) -> Any:
        """Scrape DHW Temperatures configuration data.
        
        This fetches configuration values from the DHW Temperatures page (s=4,3,0):
        - Comfort temperature
        - Eco temperature
        
        Returns a dict with DHW temperature sensor keys.
        """
        from .const import DHW_TEMPERATURES_PATH
        return await self._scrape_heating_config_page(DHW_TEMPERATURES_PATH, "DHW_TEMPS")

    async def async_scrape_dhw_standard(self) -> Any:
        """Scrape DHW Standard Setting configuration data.
        
        This fetches configuration values from the DHW Standard page (s=4,3,1):
        - DHW mode
        - DHW hysteresis
        - DHW stages
        
        Returns a dict with DHW standard setting sensor keys.
        """
        from .const import DHW_STANDARD_PATH
        return await self._scrape_heating_config_page(DHW_STANDARD_PATH, "DHW_STANDARD")

    async def async_scrape_dhw_learning(self) -> Any:
        """Scrape DHW Learning Function configuration data.
        
        This fetches configuration values from the DHW Learning page (s=4,3,2):
        - Learning function ON/OFF
        
        Returns a dict with DHW learning sensor key.
        """
        from .const import DHW_LEARNING_PATH
        return await self._scrape_heating_config_page(DHW_LEARNING_PATH, "DHW_LEARNING")

    async def async_scrape_dhw_combi_cylinder(self) -> Any:
        """Scrape DHW Combi Cylinder configuration data.
        
        This fetches configuration values from the DHW Combi Cylinder page (s=4,3,3):
        - Combi cylinder ON/OFF
        
        Returns a dict with DHW combi cylinder sensor key.
        """
        from .const import DHW_COMBI_CYLINDER_PATH
        return await self._scrape_heating_config_page(DHW_COMBI_CYLINDER_PATH, "DHW_COMBI")

    async def async_scrape_dhw_output(self) -> Any:
        """Scrape DHW Output configuration data.
        
        This fetches configuration values from the DHW Output page (s=4,3,4):
        - WW output summer
        - WW output winter
        
        Returns a dict with DHW output sensor keys.
        """
        from .const import DHW_OUTPUT_PATH
        return await self._scrape_heating_config_page(DHW_OUTPUT_PATH, "DHW_OUTPUT")

    async def async_scrape_dhw_max_flow_temp(self) -> Any:
        """Scrape DHW Maximum Flow Temperature configuration data.
        
        This fetches configuration values from the DHW Max Flow Temp page (s=4,3,5):
        - Maximum flow temperature
        
        Returns a dict with DHW max flow temp sensor key.
        """
        from .const import DHW_MAX_FLOW_TEMP_PATH
        return await self._scrape_heating_config_page(DHW_MAX_FLOW_TEMP_PATH, "DHW_MAX_FLOW")

    async def async_scrape_dhw_pasteurisation(self) -> Any:
        """Scrape DHW Pasteurisation configuration data.
        
        This fetches configuration values from the DHW Pasteurisation page (s=4,3,6):
        - Pasteurisation ON/OFF
        - Set temperature
        
        Returns a dict with DHW pasteurisation sensor keys.
        """
        from .const import DHW_PASTEURISATION_PATH
        return await self._scrape_heating_config_page(DHW_PASTEURISATION_PATH, "DHW_PASTEUR")

    async def async_scrape_dhw_external(self) -> Any:
        """Scrape DHW External Heat Source configuration data.
        
        This fetches configuration values from the DHW External page (s=4,3,7):
        - External heat source mode
        - Dual mode temperature
        - Lower application limit (optional)
        - WW PWM (optional)
        
        Returns a dict with DHW external sensor keys.
        """
        from .const import DHW_EXTERNAL_PATH
        return await self._scrape_heating_config_page(DHW_EXTERNAL_PATH, "DHW_EXTERNAL")

    async def async_scrape_sg_ready(self) -> Any:
        """Scrape SG Ready / Energy Management configuration data.
        
        This fetches configuration values from the SG Ready page (s=4,14):
        - SG Ready enabled (ON/OFF)
        - SG Ready input source (OFF/MODBUS/CAN BUS/ISG PLUS)
        - Heating buffer configuration
        - Upper temperature limits for HC1, HC2, and DHW
        
        Returns a dict with SG Ready sensor keys.
        """
        return await self._scrape_heating_config_page("/?s=4,14", "SG_READY")

    async def _scrape_heating_config_page(self, path: str, circuit: str) -> dict:
        """Generic method to scrape heating configuration pages.
        
        The ISG heating pages embed configuration values in JavaScript:
        - jsvalues array contains the actual values
        - valSettings array contains metadata (type, min, max)
        
        Args:
            path: URL path to scrape (e.g., "/?s=4,2,0")
            circuit: Circuit identifier for logging ("HC1", "HC2", "BASIC")
            
        Returns:
            dict: Extracted configuration values
        """
        page_url = f"http://{self._host}{path}"
        
        try:
            page_response = await self._api_wrapper(
                method="GET",
                url=page_url,
            )
            
            result = self._extract_heating_config(page_response, circuit)
            
        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {circuit} heating config page - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    def _extract_heating_config(self, html: str, circuit: str) -> dict:
        """Extract heating configuration values from HTML page.
        
        The configuration values are embedded in JavaScript:
        jsvalues['10976']['val']='22,0';
        valSettings['val10976']['type'] = 'float';
        
        Args:
            html: HTML page content
            circuit: Circuit identifier ("HC1", "HC2", "BASIC")
            
        Returns:
            dict: Extracted configuration values with proper types
        """
        result: dict[str, object] = {}
        
        # Parse the HTML to extract JavaScript values
        soup = bs4.BeautifulSoup(html, "html.parser")
        
        # Find all script tags and extract jsvalues
        import re
        
        # Pattern to match: jsvalues['123']['val']='value';
        val_pattern = re.compile(r"jsvalues\['(\d+)'\]\['val'\]='([^']+)';")
        # Pattern to match: valSettings['val123']['type'] = 'float';
        type_pattern = re.compile(r"valSettings\['val(\d+)'\]\['type'\]\s*=\s*'(\w+)';")
        
        # Extract all values and their types
        val_dict = {}
        type_dict = {}
        
        for script in soup.find_all("script"):
            if script.string:
                # Extract values
                for match in val_pattern.finditer(script.string):
                    val_id = match.group(1)
                    val_str = match.group(2)
                    val_dict[val_id] = val_str
                
                # Extract types
                for match in type_pattern.finditer(script.string):
                    val_id = match.group(1)
                    val_type = match.group(2)
                    type_dict[val_id] = val_type
        
        # Also extract checked radio buttons for fields without jsvalues
        # Pattern: <input ... checked="checked" ... name="val103" ... value="1"/>
        radio_inputs = soup.find_all("input", {"type": "radio", "checked": "checked"})
        for radio_input in radio_inputs:
            name = radio_input.get("name", "")
            if name.startswith("val"):
                val_id = name[3:]  # Remove "val" prefix
                value = radio_input.get("value", "")
                # Only add if not already in val_dict (jsvalues take precedence)
                if val_id not in val_dict and value:
                    val_dict[val_id] = value
                    type_dict[val_id] = "radio"
        
        LOGGER.debug("%s: Extracted values: %s", circuit, val_dict)
        LOGGER.debug("%s: Extracted types: %s", circuit, type_dict)
        
        # Map val IDs to sensor keys based on circuit
        if circuit == "HC1":
            result = self._map_hc1_values(val_dict, type_dict)
        elif circuit == "HC2":
            result = self._map_hc2_values(val_dict, type_dict)
        elif circuit == "BASIC":
            result = self._map_basic_heating_values(val_dict, type_dict)
        elif circuit == "SUMMER":
            result = self._map_summer_values(val_dict, type_dict)
        elif circuit == "PUMP_CYCLES":
            result = self._map_pump_cycles_values(val_dict, type_dict)
        elif circuit == "EXTERNAL":
            result = self._map_external_values(val_dict, type_dict)
        elif circuit == "DHW_TEMPS":
            result = self._map_dhw_temperatures_values(val_dict, type_dict)
        elif circuit == "DHW_STANDARD":
            result = self._map_dhw_standard_values(val_dict, type_dict)
        elif circuit == "DHW_LEARNING":
            result = self._map_dhw_learning_values(val_dict, type_dict)
        elif circuit == "DHW_COMBI":
            result = self._map_dhw_combi_values(val_dict, type_dict)
        elif circuit == "DHW_OUTPUT":
            result = self._map_dhw_output_values(val_dict, type_dict)
        elif circuit == "DHW_MAX_FLOW":
            result = self._map_dhw_max_flow_values(val_dict, type_dict)
        elif circuit == "DHW_PASTEUR":
            result = self._map_dhw_pasteurisation_values(val_dict, type_dict)
        elif circuit == "DHW_EXTERNAL":
            result = self._map_dhw_external_values(val_dict, type_dict)
        elif circuit == "SG_READY":
            result = self._map_sg_ready_values(val_dict, type_dict)
        
        return result

    def _map_hc1_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map HC1 val IDs to sensor keys."""
        from .const import (
            HC1_COMFORT_TEMPERATURE_KEY,
            HC1_ECO_TEMPERATURE_KEY,
            HC1_MINIMUM_TEMPERATURE_KEY,
            HC1_HEATING_CURVE_RISE_KEY,
        )
        
        result = {}
        
        # val10976 = Comfort Temperature
        if "10976" in val_dict:
            result[HC1_COMFORT_TEMPERATURE_KEY] = self._parse_value(
                val_dict["10976"], type_dict.get("10976", "float")
            )
        
        # val10977 = Eco Temperature
        if "10977" in val_dict:
            result[HC1_ECO_TEMPERATURE_KEY] = self._parse_value(
                val_dict["10977"], type_dict.get("10977", "float")
            )
        
        # val486 = Minimum Temperature (OFF = 36864)
        if "486" in val_dict:
            raw_val = val_dict["486"]
            if raw_val != "36864":  # Not OFF
                result[HC1_MINIMUM_TEMPERATURE_KEY] = self._parse_value(
                    raw_val, type_dict.get("486", "float")
                )
        
        # val25 = Heating Curve Rise
        if "25" in val_dict:
            result[HC1_HEATING_CURVE_RISE_KEY] = self._parse_value(
                val_dict["25"], type_dict.get("25", "double")
            )
        
        return result

    def _map_hc2_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map HC2 val IDs to sensor keys."""
        from .const import (
            HC2_COMFORT_TEMPERATURE_KEY,
            HC2_ECO_TEMPERATURE_KEY,
            HC2_MINIMUM_TEMPERATURE_KEY,
            HC2_MAXIMUM_TEMPERATURE_KEY,
            HC2_MIXER_DYNAMICS_KEY,
            HC2_HEATING_CURVE_RISE_KEY,
        )
        
        result = {}
        
        # val10980 = Comfort Temperature
        if "10980" in val_dict:
            result[HC2_COMFORT_TEMPERATURE_KEY] = self._parse_value(
                val_dict["10980"], type_dict.get("10980", "float")
            )
        
        # val10981 = Eco Temperature
        if "10981" in val_dict:
            result[HC2_ECO_TEMPERATURE_KEY] = self._parse_value(
                val_dict["10981"], type_dict.get("10981", "float")
            )
        
        # val487 = Minimum Temperature (OFF = 36864)
        if "487" in val_dict:
            raw_val = val_dict["487"]
            if raw_val != "36864":  # Not OFF
                result[HC2_MINIMUM_TEMPERATURE_KEY] = self._parse_value(
                    raw_val, type_dict.get("487", "float")
                )
        
        # val10982 = Maximum Temperature
        if "10982" in val_dict:
            result[HC2_MAXIMUM_TEMPERATURE_KEY] = self._parse_value(
                val_dict["10982"], type_dict.get("10982", "float")
            )
        
        # val10983 = Mixer Dynamics
        if "10983" in val_dict:
            result[HC2_MIXER_DYNAMICS_KEY] = self._parse_value(
                val_dict["10983"], type_dict.get("10983", "int")
            )
        
        # val26 = Heating Curve Rise
        if "26" in val_dict:
            result[HC2_HEATING_CURVE_RISE_KEY] = self._parse_value(
                val_dict["26"], type_dict.get("26", "double")
            )
        
        return result

    def _map_basic_heating_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map basic heating settings val IDs to sensor keys."""
        from .const import (
            HEATING_BUFFER_OPERATION_KEY,
            HEATING_MAX_RETURN_TEMP_KEY,
            HEATING_MAX_FLOW_TEMP_KEY,
            HEATING_FIXED_VALUE_OP_KEY,
            HEATING_FROST_PROTECTION_KEY,
        )
        
        result = {}
        
        # val450 = Buffer Operation (0=OFF, 1=ON)
        if "450" in val_dict:
            raw_val = val_dict["450"]
            result[HEATING_BUFFER_OPERATION_KEY] = raw_val == "1"
        
        # val11010 = Maximum Return Temperature
        if "11010" in val_dict:
            result[HEATING_MAX_RETURN_TEMP_KEY] = self._parse_value(
                val_dict["11010"], type_dict.get("11010", "float")
            )
        
        # val38 = Maximum Flow Temperature
        if "38" in val_dict:
            result[HEATING_MAX_FLOW_TEMP_KEY] = self._parse_value(
                val_dict["38"], type_dict.get("38", "float")
            )
        
        # val35 = Fixed Value Operation (OFF = 36864)
        if "35" in val_dict:
            raw_val = val_dict["35"]
            if raw_val != "36864":  # Not OFF
                result[HEATING_FIXED_VALUE_OP_KEY] = self._parse_value(
                    raw_val, type_dict.get("35", "float")
                )
        
        # val45 = Frost Protection Temperature
        if "45" in val_dict:
            result[HEATING_FROST_PROTECTION_KEY] = self._parse_value(
                val_dict["45"], type_dict.get("45", "float")
            )
        
        return result

    def _map_summer_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map summer mode val IDs to sensor keys."""
        from .const import (
            HEATING_SUMMER_MODE_KEY,
            HEATING_SUMMER_OUTSIDE_TEMP_KEY,
            HEATING_SUMMER_HEAT_BUFFER_KEY,
        )
        
        result = {}
        
        # val103 = Summer Mode (0=OFF, 1=ON)
        if "103" in val_dict:
            raw_val = val_dict["103"]
            result[HEATING_SUMMER_MODE_KEY] = raw_val == "1"
        
        # val105 = Outside Temperature
        if "105" in val_dict:
            result[HEATING_SUMMER_OUTSIDE_TEMP_KEY] = self._parse_value(
                val_dict["105"], type_dict.get("105", "float")
            )
        
        # val104 = Building Heat Buffer
        if "104" in val_dict:
            result[HEATING_SUMMER_HEAT_BUFFER_KEY] = self._parse_value(
                val_dict["104"], type_dict.get("104", "int")
            )
        
        return result

    def _map_pump_cycles_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map pump cycles val IDs to sensor keys."""
        from .const import HEATING_PUMP_CYCLES_KEY
        
        result = {}
        
        # val106 = Pump Cycles (0=OFF, 1=ON)
        if "106" in val_dict:
            raw_val = val_dict["106"]
            result[HEATING_PUMP_CYCLES_KEY] = raw_val == "1"
        
        return result

    def _map_external_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map external heat source val IDs to sensor keys."""
        from .const import (
            HEATING_EXTERNAL_SOURCE_KEY,
            HEATING_EXTERNAL_CURVE_GAP_KEY,
            HEATING_EXTERNAL_BLOCKING_TIME_KEY,
            HEATING_EXTERNAL_DUAL_MODE_TEMP_KEY,
            HEATING_EXTERNAL_LOWER_LIMIT_KEY,
        )
        
        result = {}
        
        # val342 = External Heat Source (0-4: OFF/THREADED/BOILER/PWM/0-10V)
        if "342" in val_dict:
            raw_val = val_dict["342"]
            # Map radio button index to state keys for translation
            source_map = {
                "0": "off",
                "1": "threaded_immersion_heater",
                "2": "boiler",
                "3": "hzg_pwm",
                "4": "heating_0_10v",
            }
            result[HEATING_EXTERNAL_SOURCE_KEY] = source_map.get(raw_val, raw_val)
        
        # val119 = Heating Curve Gap
        if "119" in val_dict:
            result[HEATING_EXTERNAL_CURVE_GAP_KEY] = self._parse_value(
                val_dict["119"], type_dict.get("119", "float")
            )
        
        # val374 = Blocking Time EVU
        if "374" in val_dict:
            result[HEATING_EXTERNAL_BLOCKING_TIME_KEY] = self._parse_value(
                val_dict["374"], type_dict.get("374", "int")
            )
        
        # val41 = Dual Mode Temperature HZG
        if "41" in val_dict:
            result[HEATING_EXTERNAL_DUAL_MODE_TEMP_KEY] = self._parse_value(
                val_dict["41"], type_dict.get("41", "float")
            )
        
        # val43 = Lower Application Limit HZG (OFF = 36864)
        if "43" in val_dict:
            raw_val = val_dict["43"]
            if raw_val != "36864":  # Not OFF
                result[HEATING_EXTERNAL_LOWER_LIMIT_KEY] = self._parse_value(
                    raw_val, type_dict.get("43", "float")
                )
        
        return result

    def _map_dhw_temperatures_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW temperatures val IDs to sensor keys."""
        from .const import (
            DHW_COMFORT_TEMPERATURE_KEY,
            DHW_ECO_TEMPERATURE_KEY,
        )
        
        result = {}
        
        # val11018 = Comfort Temperature
        if "11018" in val_dict:
            result[DHW_COMFORT_TEMPERATURE_KEY] = self._parse_value(
                val_dict["11018"], type_dict.get("11018", "float")
            )
        
        # val11019 = Eco Temperature
        if "11019" in val_dict:
            result[DHW_ECO_TEMPERATURE_KEY] = self._parse_value(
                val_dict["11019"], type_dict.get("11019", "float")
            )
        
        return result

    def _map_dhw_standard_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW standard setting val IDs to sensor keys."""
        from .const import (
            DHW_MODE_KEY,
            DHW_HYSTERESIS_KEY,
            DHW_STAGES_KEY,
        )
        
        result = {}
        
        # val375 = DHW Mode (0=PRIORITY, 1=PARALLEL, 2=PARTIAL PRIORITY)
        if "375" in val_dict:
            raw_val = val_dict["375"]
            mode_map = {
                "0": "priority_operation",
                "1": "parallel_operation",
                "2": "partial_priority",
            }
            result[DHW_MODE_KEY] = mode_map.get(raw_val, raw_val)
        
        # val120 = DHW Hysteresis
        if "120" in val_dict:
            result[DHW_HYSTERESIS_KEY] = self._parse_value(
                val_dict["120"], type_dict.get("120", "float")
            )
        
        # val399 = DHW Stages
        if "399" in val_dict:
            result[DHW_STAGES_KEY] = self._parse_value(
                val_dict["399"], type_dict.get("399", "int")
            )
        
        return result

    def _map_dhw_learning_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW learning function val IDs to sensor keys."""
        from .const import DHW_LEARNING_FUNCTION_KEY
        
        result = {}
        
        # val123 = WW Learning Function (0=OFF, 1=ON)
        if "123" in val_dict:
            raw_val = val_dict["123"]
            result[DHW_LEARNING_FUNCTION_KEY] = raw_val == "1"
        
        return result

    def _map_dhw_combi_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW combi cylinder val IDs to sensor keys."""
        from .const import DHW_COMBI_CYLINDER_KEY
        
        result = {}
        
        # val454 = Combi Cylinder (0=OFF, 1=ON)
        if "454" in val_dict:
            raw_val = val_dict["454"]
            result[DHW_COMBI_CYLINDER_KEY] = raw_val == "1"
        
        return result

    def _map_dhw_output_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW output val IDs to sensor keys."""
        from .const import (
            DHW_OUTPUT_SUMMER_KEY,
            DHW_OUTPUT_WINTER_KEY,
        )
        
        result = {}
        
        # val1126 = WW Output Summer
        if "1126" in val_dict:
            result[DHW_OUTPUT_SUMMER_KEY] = self._parse_value(
                val_dict["1126"], type_dict.get("1126", "int")
            )
        
        # val1127 = WW Output Winter
        if "1127" in val_dict:
            result[DHW_OUTPUT_WINTER_KEY] = self._parse_value(
                val_dict["1127"], type_dict.get("1127", "int")
            )
        
        return result

    def _map_dhw_max_flow_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW maximum flow temperature val IDs to sensor keys."""
        from .const import DHW_MAX_FLOW_TEMP_KEY
        
        result = {}
        
        # val372 = Maximum Flow Temperature
        if "372" in val_dict:
            result[DHW_MAX_FLOW_TEMP_KEY] = self._parse_value(
                val_dict["372"], type_dict.get("372", "float")
            )
        
        return result

    def _map_dhw_pasteurisation_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW pasteurisation val IDs to sensor keys."""
        from .const import (
            DHW_PASTEURISATION_KEY,
            DHW_PASTEURISATION_TEMP_KEY,
        )
        
        result = {}
        
        # val122 = Pasteurisation (0=OFF, 1=ON)
        if "122" in val_dict:
            raw_val = val_dict["122"]
            result[DHW_PASTEURISATION_KEY] = "on" if raw_val == "1" else "off"
        
        # val11033 = Set Temperature
        if "11033" in val_dict:
            result[DHW_PASTEURISATION_TEMP_KEY] = self._parse_value(
                val_dict["11033"], type_dict.get("11033", "float")
            )
        
        return result

    def _map_dhw_external_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map DHW external heat source val IDs to sensor keys."""
        from .const import (
            DHW_EXTERNAL_SOURCE_KEY,
            DHW_EXTERNAL_DUAL_MODE_TEMP_KEY,
            DHW_EXTERNAL_LOWER_LIMIT_KEY,
            DHW_EXTERNAL_PWM_KEY,
        )
        
        result = {}
        
        # val369 = External Heat Source (0=OFF, 1=SUPPORTED, 2=INDEPENDENT, 3=ALONE)
        if "369" in val_dict:
            raw_val = val_dict["369"]
            source_map = {
                "0": "OFF",
                "1": "SUPPORTED",
                "2": "INDEPENDENT",
                "3": "ALONE",
            }
            result[DHW_EXTERNAL_SOURCE_KEY] = source_map.get(raw_val, raw_val)
        
        # val42 = Dual Mode Temp WW
        if "42" in val_dict:
            result[DHW_EXTERNAL_DUAL_MODE_TEMP_KEY] = self._parse_value(
                val_dict["42"], type_dict.get("42", "float")
            )
        
        # val44 = Lower App Limit WW (OFF = 36864)
        if "44" in val_dict:
            raw_val = val_dict["44"]
            if raw_val != "36864":  # Not OFF
                result[DHW_EXTERNAL_LOWER_LIMIT_KEY] = self._parse_value(
                    raw_val, type_dict.get("44", "float")
                )
        
        # val455 = WW PWM (OFF = 36864)
        if "455" in val_dict:
            raw_val = val_dict["455"]
            if raw_val != "36864":  # Not OFF
                result[DHW_EXTERNAL_PWM_KEY] = self._parse_value(
                    raw_val, type_dict.get("455", "int")
                )
        
        return result

    def _map_sg_ready_values(self, val_dict: dict, type_dict: dict) -> dict:
        """Map SG Ready / Energy Management val IDs to sensor keys."""
        from .const import (
            SG_READY_ENABLED_KEY,
            SG_READY_INPUT_KEY,
            SG_READY_HEATING_BUFFER_KEY,
            SG_READY_UPPER_TEMP_HC1_KEY,
            SG_READY_UPPER_TEMP_HC2_KEY,
            SG_READY_UPPER_TEMP_DHW_KEY,
        )
        
        result = {}
        
        # val60305 = SG Ready Enabled (0=OFF, 1=ON)
        if "60305" in val_dict:
            result[SG_READY_ENABLED_KEY] = "ON" if val_dict["60305"] == "1" else "OFF"
        
        # val60028 = SG-Ready Input (0=OFF, 1=MODBUS, 2=CAN BUS, 3=ISG PLUS)
        if "60028" in val_dict:
            raw_val = val_dict["60028"]
            input_map = {
                "0": "OFF",
                "1": "MODBUS",
                "2": "CAN BUS",
                "3": "ISG PLUS",
            }
            result[SG_READY_INPUT_KEY] = input_map.get(raw_val, raw_val)
        
        # val60317 = Heating buffer (0=No buffer, 1=Buffer with mixer, 2=Buffer without mixer)
        if "60317" in val_dict:
            raw_val = val_dict["60317"]
            buffer_map = {
                "0": "no_buffer",
                "1": "buffer_with_mixer",
                "2": "buffer_without_mixer",
            }
            result[SG_READY_HEATING_BUFFER_KEY] = buffer_map.get(raw_val, raw_val)
        
        # val60310 = Upper Room/Buffer Temp HC1
        if "60310" in val_dict:
            result[SG_READY_UPPER_TEMP_HC1_KEY] = self._parse_value(
                val_dict["60310"], type_dict.get("60310", "float")
            )
        
        # val60311 = Upper Room Temp HC2
        if "60311" in val_dict:
            result[SG_READY_UPPER_TEMP_HC2_KEY] = self._parse_value(
                val_dict["60311"], type_dict.get("60311", "float")
            )
        
        # val60312 = Upper Set DHW Temp
        if "60312" in val_dict:
            result[SG_READY_UPPER_TEMP_DHW_KEY] = self._parse_value(
                val_dict["60312"], type_dict.get("60312", "float")
            )
        
        return result

    def _parse_value(self, value_str: str, value_type: str) -> float | int:
        """Parse a value string based on its type.
        
        Args:
            value_str: String value (e.g., "22,0" or "1,10")
            value_type: Type indicator ("int", "float", "double")
            
        Returns:
            Parsed numeric value
        """
        # Replace German decimal comma with period
        value_str = value_str.replace(",", ".")
        
        if value_type == "int":
            return int(float(value_str))
        else:  # float or double
            return float(value_str)

    def _extract_start_page(self, response: str) -> dict:
        """Extract Betriebsart from s=0 page.

        Returns a dict with key START_OPERATION_MODE_KEY when available.
        """
        soup = bs4.BeautifulSoup(response, "html.parser")
        result: dict[str, object] = {}

        # Normalize helper
        def _text(el: bs4.element.Tag | None) -> str:
            return el.get_text(strip=True) if el else ""

        # Find blocks that include h3 headings and associated '.values' or
        # '.value' elements which commonly contain the displayed value.
        # Precompute alias lists for start-page fields to use centralized mapping
        betr_aliases = get_aliases(CanonicalKey.START_OPERATION_MODE)

        for block in soup.find_all(class_=True):
            # We only care about blocks containing h3 headings
            h3 = block.find("h3")
            if not h3:
                continue
            heading = parsing._normalize_text(_text(h3))

            # Betriebsart (operation mode) — use centralized alias matching
            if parsing._matches_alias(heading, betr_aliases):
                # Map radio button value to state key
                mode_map = {
                    "0": "emergency_operation",
                    "1": "standby_mode",
                    "2": "programmed_operation",
                    "3": "comfort_mode",
                    "4": "eco_mode",
                    "5": "dhw_mode",
                }
                # Look for the hidden input that stores the selected value (id="val1")
                # This is the actual radio button value (0-5), not the display text
                hidden_input = block.find("input", attrs={"id": "val1", "type": "hidden"})
                if hidden_input and hidden_input.has_attr("value"):
                    raw_val = hidden_input.get("value")
                    result[START_OPERATION_MODE_KEY] = mode_map.get(raw_val, raw_val)
                    continue
                # Fallback: try to find the checked radio button
                checked_radio = block.find("input", attrs={"type": "radio", "checked": True})
                if checked_radio and checked_radio.has_attr("value"):
                    raw_val = checked_radio.get("value")
                    result[START_OPERATION_MODE_KEY] = mode_map.get(raw_val, raw_val)
                    continue

        # As a final fallback, try to search for these headings anywhere in the page
        # if not found by block scan above.
        if START_OPERATION_MODE_KEY not in result:
            # Fallback: find any header tag whose text matches the canonical aliases
            h = soup.find(
                lambda tag: tag.name in ("h3", "h2", "h1")
                and parsing._matches_alias(parsing._normalize_text(tag.get_text()), betr_aliases)
            )
            if h:
                # look for a following input with value
                nxt = h.find_next(lambda t: t.name == "input" and t.has_attr("value"))
                if nxt and nxt.has_attr("value"):
                    result[START_OPERATION_MODE_KEY] = nxt.get("value")

        # Portal ok indicator: some pages include a small image indicating
        # portal connectivity (e.g. <img src="pics/icon_status_ok.gif"/>).
        # Can be: pics/icon_status_ok.gif, pics/icon_status_error.gif, pics/icon_status_warning.gif
        # Expose this as a boolean key START_PORTAL_OK when icon is OK.
        try:
            # Portal ok indicator
            portal_box = soup.find(id="box_start_status_portal")
            if portal_box:
                img = portal_box.find("img")
                if img and img.has_attr("src"):
                    src = (img.get("src") or "").strip()
                    # Return state key instead of boolean
                    result[START_PORTAL_OK] = "connected" if src == "pics/icon_status_ok.gif" else "disconnected"

            # System ok indicator (similar approach)
            system_box = soup.find(id="box_start_status_system")
            if system_box:
                img = system_box.find("img")
                if img and img.has_attr("src"):
                    src = (img.get("src") or "").strip()
                    # Return state key instead of boolean
                    result[START_SYSTEM_OK] = "ok" if src == "pics/icon_status_ok.gif" else "error"

            # Energy Management status box (new since firmware update)
            # Look for div with id="Modus" that contains SG Ready information
            energy_mgmt_box = soup.find(id="Modus")
            if energy_mgmt_box:
                # Check for OK status icon
                img = energy_mgmt_box.find("img", src=lambda x: x and "icon_status" in x)
                if img and img.has_attr("src"):
                    src = (img.get("src") or "").strip()
                    is_ok = src == "./pics/icon_status_ok.gif" or src == "pics/icon_status_ok.gif"
                    result[START_ENERGY_MGMT_OK] = "OK" if is_ok else "ERROR"
                
                # Check if SG Ready logo is present
                sg_logo = energy_mgmt_box.find("img", src=lambda x: x and "SG-Ready-Logo" in x)
                result[START_SG_READY_ACTIVE] = "ON" if sg_logo is not None else "OFF"
                
                # Extract SG Ready state number from text like "Status 2 since:" or "Betriebszustand 2 seit:"
                text_content = _text(energy_mgmt_box)
                import re
                # Match various language patterns: Status/Betriebszustand/Statut d'exploitation followed by number
                state_match = re.search(r'(?:Status|Betriebszustand|Statut\s+d\'exploitation)\s+(\d+)\s+', text_content)
                if state_match:
                    result[START_SG_READY_STATE] = int(state_match.group(1))
        except Exception:
            # Keep best-effort parsing—do not fail the whole extraction on errors.
            LOGGER.debug("Failed to parse start-page ok indicators", exc_info=True)

        LOGGER.debug("Extracted data from Start page: %s", result)
        return result

    def _check_title(self, response: str) -> None:
        """Check if the title matches the expected."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        title = soup.title.string if soup.title and soup.title.string else None
        LOGGER.debug(
            "Potential ISG replied with an HTML doc containing title: %s", title
        )
        if not title or EXPECTED_HTML_TITLE not in title:
            raise StiebelEltronScrapingClientError(title or "No title found")

    def _extract_energy(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        # Delegate to parsing helper which handles alias lookup and conversion.
        return parsing.extract_energy(table, expected_header)

    def _extract_version(self, table: bs4.element.Tag) -> float | str:
        major_version, minor_version, revision = None, None, None

        # Accept both English and German labels for version rows.
        major_aliases = ["Major version", "Hauptversionsnummer", "Hauptversionsnr", "Hauptversion"]
        minor_aliases = ["Minor version", "Nebenversionsnummer", "Nebenversionsnr", "Nebenversion"]
        revision_aliases = ["Revision", "Revisionsnummer", "Revisionsnr"]

        table_rows = table.find_all("tr")
        for curr_table_row in table_rows:
            elems = curr_table_row.find_all(["td", "th"])  # type: ignore  # noqa: PGH003

            if not elems:
                continue
            texts = [elem.get_text(strip=True) for elem in elems]

            if len(texts) < 2:  # noqa: PLR2004
                continue

            key = texts[0]
            val = texts[1]

            if parsing._matches_alias(key, major_aliases):
                major_version = val
            elif parsing._matches_alias(key, minor_aliases):
                minor_version = val
            elif parsing._matches_alias(key, revision_aliases):
                revision = val

        return f"{major_version}.{minor_version}.{revision}"

    def _extract_temperature(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        """Delegate temperature extraction to parsing module."""
        return parsing.extract_temperature(table, expected_header)

    def _extract_percentage(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        """Delegate percentage extraction to parsing module."""
        return parsing.extract_percentage(table, expected_header)

    def _extract_runtime_hours(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        """Delegate runtime hours extraction to parsing module."""
        return parsing.extract_runtime_hours(table, expected_header)

    def _extract_count(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> int | None:
        """Delegate count/integer extraction to parsing module."""
        return parsing.extract_count(table, expected_header)

    def _extract_runtime_minutes(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        """Delegate runtime minutes extraction to parsing module."""
        return parsing.extract_runtime_minutes(table, expected_header)

    def _extract_info_system(self, response: str) -> dict:
        """Extract the interesting values from the Info > System page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result: dict[str, object] = {}

        # find all tables
        all_tables = soup.find_all("table")

        LOGGER.debug("Info > Heat Pump page: found %d tables", len(all_tables))

        for table_index, curr_table in enumerate(all_tables, start=1):
            all_rows = curr_table.find_all("tr")  # type: ignore  # noqa: PGH003
            all_headers = all_rows[0].find_all(["th"])  # type: ignore  # noqa: PGH003

            curr_headers = [header.get_text(strip=True) for header in all_headers]
            section_title = curr_headers[0] if curr_headers else ""

            # Snapshot keys before processing this table so we can log what it adds
            before_keys = set(result.keys())

            # Helper to check whether the current section title matches any alias
            def _section_matches(key: CanonicalKey | str) -> bool:
                # key may be a string canonical name or a CanonicalKey member.
                aliases = get_aliases(key)
                return parsing._matches_alias(section_title, aliases)

            if _section_matches(CanonicalKey.ROOM_TEMPERATURE_SECTION):
                # Use canonical alias keys (underscored) so alias lookup works for
                # localized pages (e.g., German labels). Passing the canonical
                # key into the extractor will make it consult HEADER_ALIASES.
                result[ROOM_TEMPERATURE_KEY] = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.ACTUAL_TEMPERATURE_1,
                )
                result[ROOM_HUMIDITY_KEY] = self._extract_percentage(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.RELATIVE_HUMIDITY_1,
                )
            # PROCESS_DATA_SECTION moved to the Heat Pump page: see _extract_info_heatpump
            elif _section_matches(CanonicalKey.HEATING_SECTION):
                # Prefer canonical key so alias matching picks up localized labels
                # Only set if not already present or if current value is None (allow overwriting None)
                temp = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.OUTSIDE_TEMPERATURE,
                )
                if temp is not None or OUTSIDE_TEMPERATURE_KEY not in result:
                    result[OUTSIDE_TEMPERATURE_KEY] = temp
            elif _section_matches(CanonicalKey.DHW_SECTION):
                temp = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.ACTUAL_TEMPERATURE,
                )
                if temp is not None or DHW_TEMPERATURE_KEY not in result:
                    result[DHW_TEMPERATURE_KEY] = temp
                temp = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.SET_TEMPERATURE,
                )
                if temp is not None:
                    result[DHW_SET_TEMPERATURE_KEY] = temp
            
            # Extract HK 1 (Heating Circuit 1) temperatures
            temp = self._extract_temperature(curr_table, CanonicalKey.ACTUAL_TEMPERATURE_HK_1)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[ACTUAL_TEMPERATURE_HK_1_KEY] = temp
            temp = self._extract_temperature(curr_table, CanonicalKey.SET_TEMPERATURE_HK_1)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[SET_TEMPERATURE_HK_1_KEY] = temp
            
            # Extract HK 2 (Heating Circuit 2) temperatures
            temp = self._extract_temperature(curr_table, CanonicalKey.ACTUAL_TEMPERATURE_HK_2)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[ACTUAL_TEMPERATURE_HK_2_KEY] = temp
            temp = self._extract_temperature(curr_table, CanonicalKey.SET_TEMPERATURE_HK_2)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[SET_TEMPERATURE_HK_2_KEY] = temp
            
            # Extract buffer temperatures
            temp = self._extract_temperature(curr_table, CanonicalKey.ACTUAL_BUFFER_TEMPERATURE)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[ACTUAL_BUFFER_TEMPERATURE_KEY] = temp
            temp = self._extract_temperature(curr_table, CanonicalKey.SET_BUFFER_TEMPERATURE)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[SET_BUFFER_TEMPERATURE_KEY] = temp
            
            # Extract dual mode temperatures
            temp = self._extract_temperature(curr_table, CanonicalKey.DUAL_MODE_TEMP_HZG)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[DUAL_MODE_TEMP_HZG_KEY] = temp
            temp = self._extract_temperature(curr_table, CanonicalKey.DUAL_MODE_TEMP_WW)  # type: ignore  # noqa: PGH003
            if temp is not None:
                result[DUAL_MODE_TEMP_WW_KEY] = temp

        # return the scraped data
        LOGGER.debug("Extracted data from Info > System page: %s", result)
        return result

    def _extract_info_heatpump(self, response: str) -> dict:
        """Extract the interesting values from the Info > Heat Pump page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result: dict[str, object] = {}

        # find all tables
        all_tables = soup.find_all("table")

        for table_index, curr_table in enumerate(all_tables, start=1):
            all_rows = curr_table.find_all("tr")  # type: ignore  # noqa: PGH003
            all_headers = all_rows[0].find_all(["th"])  # type: ignore  # noqa: PGH003

            curr_headers = [header.get_text(strip=True) for header in all_headers]
            section_title = curr_headers[0] if curr_headers else ""

            # Snapshot keys before processing this table so we can log what it adds
            before_keys = set(result.keys())

            def _section_matches(key: CanonicalKey | str) -> bool:
                # key may be a string canonical name or a CanonicalKey member.
                aliases = get_aliases(key)
                return parsing._matches_alias(section_title, aliases)

            if _section_matches(CanonicalKey.AMOUNT_OF_HEAT_SECTION):
                # Delegate energy/amount parsing to parsing helper and map returned
                # canonical keys to integration constants using the centralized map.
                energy_map = parsing.parse_amount_power_table(curr_table)
                for canonical, val in energy_map.items():
                    const_key = CANONICAL_TO_CONST.get(canonical)
                    if const_key is not None:
                        result[const_key] = val
            elif _section_matches(CanonicalKey.PROCESS_DATA_SECTION):
                LOGGER.debug(
                    "Info > Heat Pump: processing table %d titled '%s' as PROCESS_DATA_SECTION",
                    table_index,
                    section_title,
                )
                # Many process-level metrics appear in this table (temperatures,
                # pressures, flows, inverter stats). Delegate row parsing to the
                # pure parsing helper with section context to prevent field name conflicts.
                parsed = parsing.parse_process_data_table(
                    curr_table,
                    section_context=CanonicalKey.PROCESS_DATA_SECTION,
                )
                for matched, val in parsed.items():
                    const_key = CANONICAL_TO_CONST.get(matched)
                    if const_key is not None:
                        result[const_key] = val
            elif _section_matches(CanonicalKey.POWER_CONSUMPTION_SECTION):
                # Reuse the same parse helper for energy-like tables and map to
                # consumed keys via ENERGY_CONSUMED_MAP.
                energy_map = parsing.parse_amount_power_table(curr_table)
                for canonical, val in energy_map.items():
                    const_key = ENERGY_CONSUMED_MAP.get(canonical)
                    if const_key is not None:
                        result[const_key] = val

            elif _section_matches(CanonicalKey.EFFICIENCY_SECTION):
                LOGGER.debug("Found EFFICIENCY_SECTION in table %d ('%s')", table_index, section_title)
                # Delegate parsing of the COP-like efficiency table to a pure helper
                # that returns a small mapping of detected keys to numeric values.
                eff_parsed = parsing.parse_efficiency_table(curr_table)
                # Map helper keys to integration constants
                if CanonicalKey.HEATING_13_24 in eff_parsed:
                    result[EFFICIENCY_HEATING_13_24M_KEY] = eff_parsed.get(CanonicalKey.HEATING_13_24)
                if CanonicalKey.DHW_13_24 in eff_parsed:
                    result[EFFICIENCY_DHW_13_24M_KEY] = eff_parsed.get(CanonicalKey.DHW_13_24)
                if CanonicalKey.VD_HEATING_DAY in eff_parsed:
                    result[EFFICIENCY_HEATING_TODAY_KEY] = eff_parsed.get(CanonicalKey.VD_HEATING_DAY)
                if CanonicalKey.VD_HEATING_TOTAL in eff_parsed:
                    result[EFFICIENCY_HEATING_1_12M_KEY] = eff_parsed.get(CanonicalKey.VD_HEATING_TOTAL)
                if CanonicalKey.VD_DHW_DAY in eff_parsed:
                    result[EFFICIENCY_DHW_TODAY_KEY] = eff_parsed.get(CanonicalKey.VD_DHW_DAY)
                if CanonicalKey.VD_DHW_TOTAL in eff_parsed:
                    result[EFFICIENCY_DHW_1_12M_KEY] = eff_parsed.get(CanonicalKey.VD_DHW_TOTAL)
            elif _section_matches(CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION):
                LOGGER.debug(
                    "Info > Heat Pump: processing table %d titled '%s' as EXTERNAL_HEAT_SOURCE_SECTION",
                    table_index,
                    section_title,
                )
                # Parse external heat source (hybrid system) data with section context
                # to ensure generic field names like ISTTEMPERATUR only match external sensors
                parsed = parsing.parse_process_data_table(
                    curr_table,
                    section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION,
                )
                for matched, val in parsed.items():
                    const_key = CANONICAL_TO_CONST.get(matched)
                    if const_key is not None:
                        result[const_key] = val
            
            # Extract runtime values (hours) from any table
            runtime_hours = self._extract_runtime_hours(curr_table, CanonicalKey.RUNTIME_VD_HEATING)  # type: ignore  # noqa: PGH003
            if runtime_hours is not None:
                result[RUNTIME_VD_HEATING_KEY] = runtime_hours
            
            runtime_hours = self._extract_runtime_hours(curr_table, CanonicalKey.RUNTIME_VD_DHW)  # type: ignore  # noqa: PGH003
            if runtime_hours is not None:
                result[RUNTIME_VD_DHW_KEY] = runtime_hours
            
            runtime_hours = self._extract_runtime_hours(curr_table, CanonicalKey.RUNTIME_VD_DEFROST)  # type: ignore  # noqa: PGH003
            if runtime_hours is not None:
                result[RUNTIME_VD_DEFROST_KEY] = runtime_hours
            
            # Extract defrost time (minutes)
            defrost_mins = self._extract_runtime_minutes(curr_table, CanonicalKey.DEFROST_TIME)  # type: ignore  # noqa: PGH003
            if defrost_mins is not None:
                result[DEFROST_TIME_KEY] = defrost_mins
            
            # Extract counters
            count = self._extract_count(curr_table, CanonicalKey.DEFROST_STARTS)  # type: ignore  # noqa: PGH003
            if count is not None:
                result[DEFROST_STARTS_KEY] = count
            
            count = self._extract_count(curr_table, CanonicalKey.COMPRESSOR_STARTS)  # type: ignore  # noqa: PGH003
            if count is not None:
                result[COMPRESSOR_STARTS_KEY] = count

            # log what keys this table added (if any) to help debug missing fields
            after_keys = set(result.keys())
            added = after_keys - before_keys
            if added:
                # show a small snippet of added keys/values
                added_snapshot = {k: result.get(k) for k in sorted(added)}
                LOGGER.debug(
                    "Info > Heat Pump: table %d ('%s') added keys: %s",
                    table_index,
                    section_title,
                    added_snapshot,
                )

        # return the scraped data
        LOGGER.debug("Extracted data from Info > Heat Pump page: %s", result)
        return result

    def _extract_info_energy(self, response: str) -> dict:
        """Extract values from the Info > Energy page (s=1,8).

        The energy page shares table structures with the heat pump page (amount
        of heat / power consumption). This wrapper reuses the same parsing
        logic but adds a short debug entry point to make it obvious when the
        energy page was parsed.
        """
        LOGGER.debug("Info > Energy page: parsing s=1,8 content")
        # Reuse heatpump parsing which already understands AMOUNT_OF_HEAT
        # and POWER_CONSUMPTION sections.
        result = self._extract_info_heatpump(response)
        LOGGER.debug("Extracted data from Info > Energy page: %s", result)
        return result

    def _extract_diagnosis_system(self, response: str) -> dict:
        """Extract the interesting values from the Diagnosis > System page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result = {}

        # find all tables
        all_tables = soup.find_all("table")

        for curr_table in all_tables:
            all_rows = curr_table.find_all("tr")  # type: ignore  # noqa: PGH003
            all_headers = all_rows[0].find_all(["th"])  # type: ignore  # noqa: PGH003

            curr_headers = [header.get_text(strip=True) for header in all_headers]
            # Use normalized matching here too (some pages may localize this)
            if parsing._normalize_text(curr_headers[0]) == parsing._normalize_text("ISG"):
                result[ATTR_SW_VERSION] = self._extract_version(
                    curr_table,  # type: ignore  # noqa: PGH003
                )

        # return the scraped data
        LOGGER.debug("Extracted data from Diagnosis > System page: %s", result)
        return result

    def _extract_profile_network(self, response: str) -> dict:
        """Extract the interesting values from the Profile > Network page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result = {}

        full_text = soup.get_text()

        # First, try to find a labeled MAC field (pages often show a heading
        # like "MAC-address" with the value in a nearby element). This is more
        # reliable than blind regex scanning when the page contains multiple
        # MAC-like strings.
        def _normalize_mac(raw: str) -> str:
            # remove any separators and lowercase
            hex_only = re.sub(r"[^0-9A-Fa-f]", "", raw).lower()
            if len(hex_only) != 12:
                return ""
            # format as colon-separated lower-case pairs
            return ":".join(hex_only[i : i + 2] for i in range(0, 12, 2))

        # Search for obvious labeled fields (e.g. <h3>MAC-address</h3>) and
        # try to read a nearby element with class 'values'. Prefer these when
        # present.
        for heading in soup.find_all("h3"):
            htext = parsing._normalize_text(heading.get_text())
            if "mac" in htext:
                # Look up to the calibration block and search for a '.values' div
                calib = heading.find_parent()
                # climb until we find the calibration wrapper or run out
                for _ in range(3):
                    if calib is None:
                        break
                    # common wrapper class seen in fixtures
                    raw_classes = calib.get("class")
                    classes: list[str] = []
                    if raw_classes:
                        if isinstance(raw_classes, (list, tuple)):
                            classes = [str(c) for c in raw_classes]
                        else:
                            classes = [str(raw_classes)]
                    if any(c.startswith("calibration") for c in classes):
                        val_div = calib.find(class_="values")
                        if val_div:
                            nm = _normalize_mac(val_div.get_text(strip=True))
                            if nm:
                                result[MAC_ADDRESS_KEY] = nm
                                # Provide a small context snippet and the heading text
                                snippet = full_text[:200].replace("\n", " ")
                                LOGGER.debug("Found MAC in labeled field: %s (heading=%s)", nm, htext)
                                LOGGER.debug(
                                    "MAC candidates found on Profile > Network page (source_snippet=%s): %s",
                                    snippet,
                                    [nm],
                                )
                                return result
                            # otherwise continue searching
                        break
                    calib = calib.find_parent()

        # Look for common MAC address formats:
        #  - colon or hyphen separated pairs: XX:XX:XX:XX:XX:XX or XX-XX-..
        #  - contiguous 12 hex digits: XXXXXXXXXXXX
        mac_regex = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b|\b[0-9A-Fa-f]{12}\b")
        raw_candidates = re.findall(mac_regex, full_text)

        # Normalize and deduplicate while preserving order
        seen: set[str] = set()
        candidates: list[str] = []
        for r in raw_candidates:
            nm = _normalize_mac(r)
            if not nm:
                continue
            if nm in seen:
                continue
            seen.add(nm)
            candidates.append(nm)

        if candidates:
            # Prefer the first candidate found on the page; log all for debugging
            LOGGER.debug("MAC candidates found on Profile > Network page: %s", candidates)
            result[MAC_ADDRESS_KEY] = candidates[0]
        else:
            LOGGER.error("No MAC address found on Profile > Network page")

        # return the scraped data
        LOGGER.debug("Extracted data from Profile > Network page: %s", result)
        return result

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            headers = {"User-Agent": "StiebelEltronScrapingClient/1.0"}

            async with async_timeout.timeout(HTTP_CONNECTION_TIMEOUT):
                # Prepare a safe (truncated) representation of the payload for logging
                safe_data = None
                if data is not None:
                    try:
                        safe_data = str(data)
                        if len(safe_data) > 1000:
                            safe_data = safe_data[:1000] + "...(truncated)"
                    except Exception:
                        safe_data = "<unable to serialize payload>"

                # Log the request details at debug level. Be careful: payload may contain
                # sensitive information in some setups; we truncate large payloads above.
                LOGGER.debug(
                    "HTTP request: method=%s url=%s headers=%s payload=%s",
                    method,
                    url,
                    headers,
                    safe_data,
                )

                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)

                # Read full response text, then log a truncated snippet for debugging.
                # Try UTF-8 first, fall back to ISO-8859-1 if that fails (for German umlauts etc.)
                try:
                    text = await response.text(encoding='utf-8')
                except UnicodeDecodeError:
                    text = await response.text(encoding='iso-8859-1')
                safe_text = text if isinstance(text, str) else str(text)
                if len(safe_text) > 1000:
                    safe_text = safe_text[:1000] + "...(truncated)"

                msg_template = (
                    "HTTP response: method=%s url=%s status=%s response_snippet=%s"
                )
                LOGGER.debug(msg_template, method, url, response.status, safe_text)

                return text

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise StiebelEltronScrapingClientCommunicationError(
                msg,
            ) from exception

        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise StiebelEltronScrapingClientCommunicationError(
                msg,
            ) from exception
