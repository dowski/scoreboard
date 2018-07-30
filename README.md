# Digital Baseball Scoreboard

The software to power my digital baseball scoreboard. A custom board is
required for the software to really do anything.

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
python -m scoreboard.scoreboard <Uppercase Team Name>
```

e.g.

```
python -m scoreboard.scoreboard Indians
```

## Running the tests

This project uses pytest for tests. The following command should install
pytest and run the tests.

```
python setup.py test
```

## Built With

* [mlbgame](http://panz.io/mlbgame/) - Library for accessing MLB game data
* [gpiozero](https://gpiozero.readthedocs.io/) - Hardware interface library for the Raspberry Pi

## Authors

* **Christian Wyglendowski** 

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
