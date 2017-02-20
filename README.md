# OpenFisca France

[![Join the chat at https://gitter.im/openfisca/openfisca-france](https://badges.gitter.im/openfisca/openfisca-france.svg)](https://gitter.im/openfisca/openfisca-france?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Build Status](https://travis-ci.org/openfisca/openfisca-france.svg?branch=master)](https://travis-ci.org/openfisca/openfisca-france)

[More build statuses](http://www.openfisca.fr/build-status)

[OpenFisca](http://www.openfisca.fr/) is a versatile microsimulation free software.
This is the source code of the France module.

The documentation of the project is hosted at http://doc.openfisca.fr/

## Contributors

Initial developers: Clément Schaff and Mahdi Ben Jelloul.

OpenFisca Team:
  - Mahdi Ben Jelloul
  - Christophe Benz
  - Claire Bernard
  - Léo Bouloc
  - Laurence Bouvard
  - Grégory Cornu
  - Sophie Cottet
  - Pierre-Yves Cusset
  - Félix Defrance
  - Jérôme Desbœufs
  - Sarah Dijols
  - Thomas Douenne
  - Alexis Eidelman
  - Adrien Fabre
  - Emmanuel Gratuze
  - Malka Guillot
  - Arnaud Kleinpeter
  - Victor Le Breton
  - Marion Monnet
  - Adrien Pacifico
  - Florian Pagnoux
  - Louise Paul-Delvaux
  - Emmanuel Raviart
  - Lucile Romanello
  - Stanislas Rybak
  - Jérôme Santoul
  - Clément Schaff
  - Matti Schneider
  - Romain Soufflet
  - Maël Thomas
  - Suzanne Vergnolle

Special thanks to:
  - Antoine Bozio
  - Fabien Dell
  - Pierre Pezziardi
  - Alain Trannoy

### Run with the Web API

```sh
pip install OpenFisca-Web-API[paster]
paster serve api/api_config.ini
```

To test with sample files:

```sh
curl http://localhost:2000/api/1/calculate -X POST --data @./api/examples/calculate_single_person_1.json --header 'content-type: application/json' | jq .
curl http://localhost:2000/api/1/simulate -X POST --data @./api/examples/simulate_single_person_1.json --header 'content-type: application/json' | jq .
```

> Here we use [`curl`](http://curl.haxx.se/) to perform HTTP requests and [`jq`](https://stedolan.github.io/jq/)
> to format the JSON payload of the HTTP response:
