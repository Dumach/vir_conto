# VIR Conto


### Business Intelligence for C-Conto

![vir-ui-wireframe](https://github.com/user-attachments/assets/72824184-b95a-4124-a412-e996f4bc23b0)


## VIR Conto

VIR Conto is an app which integrates data coming from C-Conto to Frappe Framework and utilise Frappe's Insights to create insightful charts.


## Requirements

Recommendend Python version: **3.10+**

1. Install [Frappe Framework](https://github.com/frappe/frappe) - [docs](https://docs.frappe.io/framework/user/en/installation)
2. In order to visualize data, install [Frappe Insights](https://github.com/frappe/insights) with `bench get-app insights`
3. We recommend switching to **stable** versions in all Frappe products (Framework, Insights) as well with VIR Conto


## Installation

You can install vir_conto app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Dumach/vir_conto --branch main
```

To install a specific version:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Dumach/vir_conto --branch version-0.1.0
```

Sometimes extra dependencies needed or JavaScirpt files missing, we recommend to run:
```bash
bench setup requirements
```


### Installing on a Frappe site

Before installing VIR Conto on a site, you will need to provide a `.env` file **in the site folder** (`your-bench-path/sites`).

We provide an example environment variable called `example.env`, We recommend to change the **VIR_CONTO** system user *email address* to your domain.

1. To install VIR Conto on a site:
```bash
bench --site your.site.com install-app vir_conto
```
2. Find `key.json` inside your site folder `your-bench-path/sites/your.site.com` which stores the API key and API secret.
3. Update SYS.ini in C-Conto with the **API** key, secret and your domain(`http://your.site.com`)

When successfully installed, VIR Conto will create a system user which will be used to send data from C-Conto to your site.



## Contributing

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


## License

agpl-3.0
