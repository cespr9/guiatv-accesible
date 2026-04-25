import streamlit as st
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

st.set_page_config(page_title="Guía TV Accesible", page_icon="📺")

def obtener_fecha(cadena_xml):
    fecha_limpia = cadena_xml.split(" ")[0]
    return datetime.strptime(fecha_limpia, "%Y%m%d%H%M%S")
@st.cache_data(ttl=3600)

def descargar_xml():
    url = "https://raw.githubusercontent.com/davidmuma/EPG_dobleM/master/guiatv.xml"
    respuesta = requests.get(url)
    return respuesta.content

def procesar_guia():
    contenido_xml = descargar_xml()
    root = ET.fromstring(contenido_xml)
    
    canales_interes = {
    "La 1 HD": "La 1",
    "La 2": "La 2",
    "Antena 3 HD": "Antena 3",
    "Telecinco HD": "Telecinco",
    "Cuatro HD": "Cuatro",
    "La Sexta HD": "La Sexta",
    "Teledeporte": "Teledeporte",
    "Telemadrid": "Telemadrid"

    }
    guia_por_dias = {}
    
    ahora_utc = datetime.now(timezone.utc)
    ahora_espana = ahora_utc + timedelta(hours=2)
    ahora = ahora_espana.replace(tzinfo=None)

    for programa in root.findall('programme'):
        canal_id = programa.get('channel')
        
        if canal_id in canales_interes:
            nombre_canal = canales_interes[canal_id]
           
            fin_dt = obtener_fecha(programa.get('stop'))
            
            if fin_dt < ahora:
                continue
                
            inicio_dt = obtener_fecha(programa.get('start'))
            dia_texto = inicio_dt.strftime("%d/%m/%Y")
            
            if dia_texto not in guia_por_dias:
                guia_por_dias[dia_texto] = {}
                
            if nombre_canal not in guia_por_dias[dia_texto]:
                guia_por_dias[dia_texto][nombre_canal] = []
            
            hora_str = inicio_dt.strftime("%H:%M")
            titulo = programa.find('title').text
            
            guia_por_dias[dia_texto][nombre_canal].append(f"**{hora_str}** - {titulo}")
            
    return guia_por_dias

st.title("📺 Guía de TV Accesible")

with st.spinner("Descargando y filtrando la programación actual..."):
    datos_tv = procesar_guia()

if datos_tv:
    dias_disponibles = list(datos_tv.keys())
    pestanas = st.tabs(dias_disponibles)
    
    for i, dia in enumerate(dias_disponibles):
        with pestanas[i]:
            for canal, programas in datos_tv[dia].items():
                with st.expander(f"{canal}", expanded=False):
                    st.markdown("\n\n".join(programas))
else:
    st.error("No hay programación disponible o hubo un error al cargar.")