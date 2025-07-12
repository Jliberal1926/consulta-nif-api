from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

@app.route('/')
def home():
    return '✅ API de Consulta NIF está online!'

@app.route('/consulta')
def consulta():
    nif = request.args.get("nif")
    if not nif:
        return jsonify({"status": "erro", "mensagem": "NIF não fornecido"}), 400

    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 15)

        driver.get("https://portaldocontribuinte.minfin.gov.ao/consultar-nif-do-contribuinte")

        input_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@id, 'txtNIFNumber')]")))
        input_field.send_keys(nif)

        botao_pesquisar = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Pesquisar']]")))
        botao_pesquisar.click()
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

        if not nome:
            return jsonify({"status": "erro", "mensagem": "NIF não encontrado ou a página mudou"})

        return jsonify({
            "status": "ok",
            "nome": nome,
            "tipo": tipo,
            "nif": nif,
            "estado": estado,
            "regime_iva": regime_iva
        })

    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro ao buscar dados: {str(e)}"}), 500
