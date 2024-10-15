
import configparser
from pathlib import Path


# Carrega arquivo de propriedades
properties_file = "config.properties"

# Caminho do script atual
current_path = Path(__file__).resolve()

# Caminho diretório pai
parent_dir = current_path.parent.parent

# Caminho completo
config_path = parent_dir / properties_file

def read_properties(arquivo):
    config = configparser.ConfigParser()
    config.read(arquivo)
    return config

properties = read_properties(config_path)