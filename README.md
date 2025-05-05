### Vir Conto

Business Intelligence for Cconto

---------------------
### Application still in early alpha !
---------------------

### Requirements

In order to visualize data, install [Frappe Insights](https://github.com/frappe/insights) as well

Tested python versions are: `3.10` and `3.12`

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Dumach/vir_conto --branch main
bench install-app vir_conto
```

To install a specific version:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Dumach/vir_conto --branch version-0.1.0
bench install-app vir_conto
```

After install run, in order to install extra dependencies and build JavaScript source files:
```
bench setup requirements
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/vir_conto
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade


### License

agpl-3.0
