import requests
import logging
from datetime import timedelta
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_TOKEN
from homeassistant.util import Throttle
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

# Minimální doba mezi aktualizacemi senzorů
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=60)
_LOGGER = logging.getLogger(__name__)

DOMAIN = "golemio"
CONF_NAME = "name"
CONF_CONTAINERID = "container_id"
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_CONTAINERID): cv.string,
    }
)

# Funkce pro nastavení platformy
def setup_platform(hass, config, add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    token = config.get(CONF_TOKEN)
    containerid = config.get(CONF_CONTAINERID)
    entities = []
    
    # Získání dat z API
    response_data = call_api_get(token, containerid)
    if response_data:
        containers = response_data["features"][0]["properties"]["containers"]
        for i, container in enumerate(containers):
            # Přidání senzoru pouze pokud existují klíče "next_pick" a "percent_calculated"
            if "next_pick" in container["cleaning_frequency"] and "last_measurement" in container:
                entities.append(GolemSensor(hass, name, i, container, token, containerid, "next_pick", "Next Pick"))
                entities.append(GolemSensor(hass, name, i, container, token, containerid, "percent_calculated", "Percent Calculated"))
    
    add_entities(entities)

# Funkce pro získání dat z API
def call_api_get(token, containerid):
    api_headers = {
        "accept": "application/json",
        "X-Access-Token": token
    }
    api_params = {"id": containerid}
    url = "https://api.golemio.cz/v2/sortedwastestations"
    try:
        response = requests.get(url, headers=api_headers, params=api_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        _LOGGER.error("Chyba při volání API: %s", e)
        return None

# Třída pro senzor
class GolemSensor(SensorEntity):
    def __init__(self, hass, name, index, container, token, containerid, data_key, friendly_name):
        """Inicializace senzoru."""
        self.hass = hass
        self._name = name
        self._index = index
        self._container = container
        self._token = token
        self._containerid = containerid
        self._data_key = data_key
        self._friendly_name = friendly_name
        self.update()

    # Unikátní ID senzoru
    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._friendly_name.lower().replace(' ', '_')}_{self._index}"

    # Ikona senzoru
    @property
    def icon(self):
        if self._data_key == "next_pick":
            return "mdi:home-clock" 
        elif self._data_key == "percent_calculated":
            return "mdi:percent"

    @property
    def should_poll(self):
        return True
    
    # Název senzoru
    @property
    def name(self):
        if self._data_key == "next_pick":
            data_name = "Next Pick"
        elif self._data_key == "percent_calculated":
            data_name = "Percent Calculated"
        else:
            data_name = "Unknown Data"

        return f"{self._name} {data_name} {self._index}"
    
    # Přátelský název senzoru
    @property
    def friendly_name(self):
        if self._data_key == "next_pick":
            data_name = "Next Pick"
        elif self._data_key == "percent_calculated":
            data_name = "Percent Calculated"
        else:
            data_name = "Unknown Data"

        return f"{data_name} {self._index}"

    # Hodnota senzoru
    @property
    def native_value(self):
        if self._data_key == "next_pick":
            # Vrátí hodnotu klíče "next_pick" nebo "n/a" pokud neexistuje
            return self._container["cleaning_frequency"].get(self._data_key, "n/a")
        elif self._data_key == "percent_calculated":
            # Vrátí hodnotu klíče "percent_calculated" nebo "n/a" pokud neexistuje
            return self._container["last_measurement"].get(self._data_key, "n/a")
        
        return "n/a"

    @Throttle(MIN_TIME_BETWEEN_SCANS)
    def update(self):
        response_data = call_api_get(self._token, self._containerid)
        if response_data:
            self._container = response_data["features"][0]["properties"]["containers"][self._index]
