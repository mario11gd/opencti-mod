from pycti import *
import json
import re
from datetime import datetime
import subprocess
import sys

try:
    import matplotlib.pyplot as plt 
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

api_url = "http://138.4.27.55:8080/"
api_token = "1de472a6-c8cd-404f-89b3-de7bf1e5b8da"
opencti = OpenCTIApiClient(api_url, api_token)

def asignar_riesgo(amenaza, riesgo):
  amenaza_manager = IntrusionSet(opencti)
  riesgo_manager = Label(opencti)
  amenaza_id = amenaza_manager.list(search=amenaza)[0]["id"]
  for i in range(10):
      if riesgo_manager.list(search=riesgo)[i]["value"] == riesgo:
          riesgo_id = riesgo_manager.list(search=riesgo)[i]["id"]
          break
  mutation = """
  mutation AddLabelToIntrusionSet($id: ID!, $toId: StixRef!) {
    intrusionSetEdit(id: $id) {
      relationAdd(input: {toId: $toId, relationship_type: "object-label"}) {
        id
      }
    }
  }
  """
  mutation_variables = {"id": amenaza_id, "toId": riesgo_id}
  opencti.query(mutation, mutation_variables)
  return

def eliminar_riesgo(amenaza, riesgo):
  amenaza_manager = IntrusionSet(opencti)
  riesgo_manager = Label(opencti)
  amenaza_id = amenaza_manager.list(search=amenaza)[0]["id"]
  for i in range(10):
      if riesgo_manager.list(search=riesgo)[i]["value"] == riesgo:
          riesgo_id = riesgo_manager.list(search=riesgo)[i]["id"]
          break
  mutation = """
  mutation RemoveLabelFromIntrusionSet($id: ID!, $toId: StixRef!) {
    intrusionSetEdit(id: $id) {
      relationDelete(toId: $toId, relationship_type: "object-label") {
        id
      }
    }
  }
  """
  mutation_variables = {"id": amenaza_id, "toId": riesgo_id}
  opencti.query(mutation, mutation_variables)
  return

def actualizar_riesgo(amenaza, riesgo):
  amenaza_manager = IntrusionSet(opencti)
  amenaza_riesgos = amenaza_manager.list(search=amenaza)[0]["objectLabel"]
  if amenaza_riesgos != []:
    for i in amenaza_riesgos:
      eliminar_riesgo(amenaza,i["value"])
  asignar_riesgo(amenaza,riesgo)  
  return

def obtener_hist_riesgos(amenaza):
  logs_query = """
  query GetLogs {
      logs {
          edges {
              node {
                  timestamp
                  raw_data
              }
          }
      }
  }
  """
  logs_data = opencti.query(logs_query)
  logs = logs_data.get("data", {}).get("logs", {}).get("edges", [])
  plot_data= {}
  if logs:
      for log in logs:
          data = json.loads(log["node"]["raw_data"])
          if "entity_name" in data["context_data"].keys():
            if data["context_data"]["entity_name"] == amenaza and "adds" in data["context_data"]["message"]: 
              match = re.search(r'`(\d+)`', data["context_data"]["message"])
              if match:
                plot_data[datetime.strptime(data["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")] = match.group(1)
  return plot_data

def graficar_riesgo(amenaza, n_medidas):
  clave = 0
  while clave == 0:
    try:
      plot_data = obtener_hist_riesgos(amenaza)
      clave = 1
    except:
      pass
  x = list(plot_data.keys())[:n_medidas]
  y = [int(value) for value in plot_data.values()][:n_medidas]
  print(x,y)

  plt.figure(figsize=(10, 6))
  plt.plot(x, y, marker='o', linestyle='-', color='b')

  plt.title('Evolución del riesgo asociado a ' + amenaza)
  plt.xlabel('Fecha y hora')
  plt.ylabel('Valor')
  plt.yticks([1, 2, 3, 4, 5])
  plt.xticks(rotation=45)
  plt.grid(True)
  plt.savefig("grafica.png")

if __name__ == "__main__":
  pass