from pycti import *

# Configuración de la conexión con el servidor OpenCTI
api_url = "http://138.4.27.55:8080/"
api_token = "1de472a6-c8cd-404f-89b3-de7bf1e5b8da"
opencti = OpenCTIApiClient(api_url, api_token)

def importar_incidente(individual):
    """
    Crea un incidente en OpenCTI a partir de los datos proporcionados.
    Relaciona el incidente con infraestructuras afectadas utilizando relaciones 'compromises'.
    
    Args:
        individual (dict): Diccionario con los detalles del incidente a crear.
    
    Returns:
        tuple: ID del incidente creado y el tipo ("Incidente").
    """
    incident = Incident(opencti)
    
    # Verifica si el incidente ya existe; si no, lo crea
    if incident.list(search=individual["id"]) == []:
        print("--- Creando incidente " + individual["id"])
        
        # Crea el incidente con los datos proporcionados
        incident.create(
            name=individual["id"],
            incident_type=individual["tipo"][0]
        )
        
        # Recupera el ID del incidente recién creado
        incident_id = incident.list(search=individual["id"])[0]["id"]
        
        # Relaciona el incidente con infraestructuras afectadas
        for activo in individual["activo_afectado"]: 
            infrastructure = Infrastructure(opencti)
            relationship = StixCoreRelationship(opencti)
            try:
                # Busca la infraestructura afectada
                infrastructure_id = infrastructure.list(search=activo)[0]["id"]
                
                # Crea la relación 'compromises' entre el incidente y la infraestructura
                relationship.create(
                    fromId=incident_id,
                    toId=infrastructure_id, 
                    relationship_type="compromises"
                )
            except:
                pass  # Maneja casos donde la infraestructura no existe o no puede relacionarse

        print("--- Incidente " + individual["id"] + " creado")
        return (incident_id, "Incidente")

def importar_activo(individual):
    """
    Crea activos en OpenCTI (localizaciones, identidades, infraestructuras) 
    según los datos proporcionados, y establece relaciones con usuarios si corresponde.
    
    Args:
        individual (dict): Diccionario con los detalles del activo a crear.
    
    Returns:
        tuple: ID del activo creado y su tipo ("Location", "Identity", "Infrastructure").
    """
    if "Location_Utilities" in individual["clases"]:
        print("--- Creando localización " + individual["id"])
        location = Location(opencti)
        
        # Crea una localización (ejemplo: ciudad) con los datos proporcionados
        location.create(
            name=individual["id"],
            description=individual["description"][0],
            type="City"
        )
        
        # Recupera el ID de la localización recién creada
        location_id = location.list(search=individual["id"])[0]["id"]
        
        # Relaciona la localización con usuarios relacionados
        for user in individual["related"]:
            if "User" in user:
                identity = Identity(opencti)
                relationship = StixCoreRelationship(opencti)
                try:
                    user_id = identity.list(search=user)[0]["id"]
                    relationship.create(
                        fromId=user_id,
                        toId=location_id, 
                        relationship_type="located-at"
                    )
                except:
                    pass  # Maneja errores en caso de que el usuario no exista o no pueda relacionarse

        print("--- Localización " + individual["id"] + " creada")
        return (location_id, "Location")
    
    elif "Personnel" in individual["clases"]:
        print("--- Creando identidad " + individual["id"])
        identity = Identity(opencti)
        
        # Crea una identidad de tipo 'Individual'
        identity.create(
            type="Individual",
            name=individual["id"],
            description=individual["description"][0]
        )
        
        identity_id = identity.list(search=individual["id"])[0]["id"]
        print("--- Identidad " + individual["id"] + " creada")
        return (identity_id, "Identity")
    
    elif "Infrastructure" in individual["clases"]:
        print("--- Creando infraestructura " + individual["id"])
        infrastructure = Infrastructure(opencti)
        
        # Crea una infraestructura con los datos proporcionados (si tiene descripción)
        if individual["description"] != []:
            infrastructure.create(
                name=individual["id"],
                description=individual["description"][0]
            )
        else:
            infrastructure.create(name=individual["id"])
        
        # Recupera el ID de la infraestructura recién creada
        infrastructure_id = infrastructure.list(search=individual["id"])[0]["id"]
        
        # Relaciona la infraestructura con usuarios relacionados
        for user in individual["related"]:
            if "User" in user:
                identity = Identity(opencti)
                relationship = StixCoreRelationship(opencti)
                try:
                    user_id = identity.list(search=user)[0]["id"]
                    relationship.create(
                        fromId=infrastructure_id,
                        toId=user_id, 
                        relationship_type="related-to"
                    )
                except:
                    pass

        print("--- Infraestructura " + individual["id"] + " creada")
        return (infrastructure_id, "Infrastructure")

def importar_amenaza(individual):
    """
    Crea una amenaza como 'IntrusionSet' en OpenCTI y la relaciona con infraestructuras afectadas.
    
    Args:
        individual (dict): Diccionario con los detalles de la amenaza a crear.
    
    Returns:
        tuple: ID de la amenaza creada y su tipo ("Amenaza").
    """
    print("--- Creando amenaza " + individual["id"])
    amenaza = IntrusionSet(opencti)
   
    amenaza.create(
        name=individual["id"],
        description=" - ".join(individual["clases"]) +
                    f" | Probabilidad: {individual['probabilidad']} | Impacto: {individual['impacto']}"
    )
    
    amenaza_id = amenaza.list(search=individual["id"])[0]["id"]
    
    # Relaciona la amenaza con infraestructuras afectadas
    for activo in individual["activo_afectado"]: 
        infrastructure = Infrastructure(opencti)
        relationship = StixCoreRelationship(opencti)
        try:
            infrastructure_id = infrastructure.list(search=activo)[0]["id"]
            relationship.create(
                fromId=amenaza_id,
                toId=infrastructure_id, 
                relationship_type="compromises"
            )
        except:
            pass

    print("--- Amenaza " + individual["id"] + " creada")
    return (amenaza_id, "Amenaza")

def importar_riesgo(individual):
    """
    Crea o recupera una etiqueta de riesgo en OpenCTI.
    
    Args:
        individual (dict): Diccionario con los detalles del riesgo.
    
    Returns:
        tuple: ID del riesgo creado/recuperado y su tipo ("Riesgo").
    """
    label = Label(opencti)
        
    asociated_color = {
        "1": "green",  # Riesgo bajo
        "2": "blue",   # Riesgo leve
        "3": "yellow", # Riesgo moderado
        "4": "orange", # Riesgo alto
        "5": "red"    # Riesgo muy alto
    }

    if label.list(search=individual["nivel_riesgo"]) != []:
        if label.list(search=individual["nivel_riesgo"])[0]["value"] == individual["nivel_riesgo"]:
            label.create(
                value=individual["nivel_riesgo"], 
                color=asociated_color[individual["nivel_riesgo"]]
            )
            return
        
    print("--- Creando riesgo " + individual["nivel_riesgo"])
    label.create(
        value=individual["nivel_riesgo"], 
        color=asociated_color[individual["nivel_riesgo"]]
    )
    
    # Recupera el ID de la etiqueta
    label_id = label.list(search=individual["nivel_riesgo"])[0]["id"]
    return (label_id, "Riesgo")

if __name__ == "__main__":
    print("Conexión establecida")
    importar_incidente({
            "id": "Incident_prueba",
            "tipo": [
                "Incident"
            ],
            "activo_afectado": [
                "Plane1"
            ]
        })