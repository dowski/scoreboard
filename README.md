# Digital Baseball Scoreboard

The software to power a digital baseball scoreboard. Once started, it will
follow the schedule for the team of your choosing and fetch data and display live
details during games.

## Getting Started

These instructions will get you a copy of the project up and running on
your local machine for development and testing purposes. See deployment for
notes on how to deploy the project on a live system.

### Installing

To simply install the package, run:

```
python setup.py install
```

After it's installed, you can run the following command to start the software:

```
scoreboard <Uppercase Team Name>
```

e.g.

```
scoreboard Indians
```

## Running the tests

This project uses pytest for tests. The following command should install
pytest and run the tests.

```
python setup.py test
```

## Built With

* [MLB-StatsAPI](https://github.com/toddrob99/MLB-StatsAPI) - Library for accessing MLB game data
* [gpiozero](https://gpiozero.readthedocs.io/) - Hardware interface library for the Raspberry Pi
* [luma.led_matrix](https://github.com/rm-hull/luma.led_matrix) - A library to drive displays using the MAX7219 LED driver
* [python-dateutil](https://pypi.org/project/python-dateutil/) - Useful time/date functionality to complement the standard library `datetime` library

## Authors

* **Christian Wyglendowski** 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
