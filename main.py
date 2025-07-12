# -- coding: utf-8 --
import sys
import io
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Garante que a saída padrão seja UTF-8 (Windows)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Recebe o NIF como argumento
if len(sys.argv) < 2:
    print(json.dumps({"status": "erro", "mensagem": "NIF não fornecido"}))
    sys.exit()

nif = sys.argv[1]

# Configuração do Chrome headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Inicializa com ChromeDriver compatível
service = Service(ChromeDriverManager().install())

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://portaldocontribuinte.minfin.gov.ao/consultar-nif-do-contribuinte")

    # Espera o campo de NIF aparecer
    input_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'txtNIFNumber')]")))
    input_field.send_keys(nif)

    # Espera o botão 'Pesquisar' aparecer pelo texto
    botao_pesquisar = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[.//span[text()='Pesquisar']]")
    ))
    botao_pesquisar.click()

    # Aguarda os dados carregarem
    time.sleep(4)

    def extrair(xpath):
        try:
            return driver.find_element(By.XPATH, xpath).text.strip()
        except:
            return ""

    nome = extrair("//label[contains(text(), 'Nome')]/following::div[1]")
    tipo = extrair("//label[contains(text(), 'Tipo')]/following::div[1]")
    estado = extrair("//label[contains(text(), 'Estado')]/following::div[1]")
    regime_iva = extrair("//label[contains(text(), 'Regime de IVA')]/following::div[1]")

    driver.quit()

    if not nome and not tipo:
        print(json.dumps({"status": "erro", "mensagem": "NIF não encontrado ou página mudou"}))
    else:
        print(json.dumps({
            "status": "ok",
            "nome": nome,
            "tipo": tipo,
            "nif": nif,
            "estado": estado,
            "regime_iva": regime_iva
        }, ensure_ascii=False))

except Exception as e:
    print(json.dumps({"status": "erro", "mensagem": str(e)}))
    try:
        driver.quit()
    except:
        pass
