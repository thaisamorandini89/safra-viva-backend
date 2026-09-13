# SafraViva Backend

## Overview
SafraViva is a backend application designed to manage agricultural properties and related entities. It provides a RESTful API for handling various resources such as agricultural companies, tax regimes, types of companies, soil types, land use capability classes, and properties.

## Project Structure
```
safraviva-backend
├── app.py
├── models
│   ├── __init__.py
│   ├── empresa_agricola.py
│   ├── regime_tributario.py
│   ├── tipo_empresa.py
│   ├── tipo_solo.py
│   ├── classe_capacidade_uso.py
│   └── propriedade.py
├── services
│   ├── __init__.py
│   ├── empresa_agricola_service.py
│   ├── regime_tributario_service.py
│   ├── tipo_empresa_service.py
│   ├── tipo_solo_service.py
│   ├── classe_capacidade_uso_service.py
│   └── propriedade_service.py
├── controllers
│   ├── __init__.py
│   ├── geo_controller.py
│   ├── empresa_agricola_controller.py
│   ├── regime_tributario_controller.py
│   ├── tipo_empresa_controller.py
│   ├── tipo_solo_controller.py
│   ├── classe_capacidade_uso_controller.py
│   └── propriedade_controller.py
├── migrations
│   ├── versions
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd safraviva-backend
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   Update the `SQLALCHEMY_DATABASE_URI` in `app.py` with your database credentials.

5. **Run migrations**
   ```bash
   flask db upgrade
   ```

6. **Start the application**
   ```bash
   python app.py
   ```

## Usage
The API provides endpoints for managing properties and related entities. You can access the API at `http://localhost:5000/api`.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.