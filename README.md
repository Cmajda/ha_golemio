# ha_golemio
Beta Version  
## Krok 1 - Registrace api golemio:
Registrace: [https://api.golemio.cz/api-keys/auth/sign-up](https://api.golemio.cz/api-keys/auth/sign-up)  
## krok 2 - Zjištěni ID kontejneru:
Nalezení kontejner id:  
[https://api.golemio.cz/v2/docs/openapi/#/](https://api.golemio.cz/v2/docs/openapi/#/)

## Krok 3 - Konfigurace HA:  
- vložit token do seacret.yaml
	```yaml 
	golemio: "<TOKEN>"
	```
- nakonfigurovat senzor configuration.yaml
	```yaml 
	- platform: golemio
	  name: conc
	  token: !secret golemio
	  container_id: 2075
	```
- Restartovat HA
- Vytvořit kartu entity (příklad záleží na počtu kontejnerů)
	```yaml 
	type: entities
	entities:
	  - sensor.conc_next_pick_0
	  - sensor.conc_percent_calculated_0
	  - sensor.conc_next_pick_1
	  - sensor.conc_percent_calculated_1
	  - sensor.conc_next_pick_2
	  - sensor.conc_percent_calculated_2
	  - sensor.conc_next_pick_3
	  - sensor.conc_percent_calculated_3
	  - sensor.conc_next_pick_4
	  - sensor.conc_percent_calculated_4
	  - sensor.conc_next_pick_5
	  - sensor.conc_percent_calculated_5
	  - sensor.conc_next_pick_6
	  - sensor.conc_percent_calculated_6
	```