# AgentUP — Documento de referencia para CV y portafolio

> Documento interno de apoyo. Reúne, en formato narrativo, qué es AgentUP, cómo
> se construyó, qué decisiones técnicas hubo detrás y qué impacto tendría en un
> contexto empresarial real. No es documentación del producto (para eso está el
> `README.md`): es material para redactar el CV, la ficha de portafolio y para
> hablar del proyecto en una entrevista.

---

## 1. Qué es AgentUP

**AgentUP** es un agente de inteligencia artificial corporativo que responde
preguntas en lenguaje natural sobre la documentación interna de una empresa.
Se construyó como challenge final del programa de Alura, y el caso de uso
elegido fue **NovaDesk**, un SaaS ficticio de mesa de ayuda para el que se
generó un corpus documental coherente: base de conocimiento del producto,
términos de uso, planes y precios, catálogo de integraciones y preguntas
frecuentes de soporte.

El problema que resuelve es uno muy concreto y muy común en cualquier empresa
con más de veinte personas: **el conocimiento existe, pero está disperso**. Está
repartido entre un PDF de producto, una hoja de cálculo de precios, un HTML de
FAQ del soporte y un Markdown legal que nadie recuerda dónde vive. Cuando un
colaborador nuevo pregunta "¿qué incluye el plan Pro?" o "¿cuál es la política
de reembolso?", la respuesta existe, pero cuesta encontrarla, y termina
consumiendo el tiempo de una persona senior que sí lo sabe.

AgentUP convierte ese corpus disperso en una **base de conocimiento
conversacional**. El usuario abre una URL, escribe la pregunta en lenguaje
natural y recibe una respuesta redactada **más la lista de documentos de los que
se extrajo**. Si la respuesta no está en la documentación, el agente lo dice
explícitamente en lugar de inventar.

El proyecto está desplegado públicamente en Google Cloud Run y es accesible sin
autenticación:
**https://agentup-382104851468.us-central1.run.app**

### El diferenciador: trazabilidad y control de alucinaciones

La parte que más define el proyecto no es que "responda preguntas" —eso lo hace
cualquier chatbot— sino **que solo responda lo que puede probar**. Cada
respuesta viene acompañada de sus fuentes, y el sistema está diseñado para
reconocer cuándo no sabe algo.

Ejemplo real del sistema en producción:

| Pregunta | Respuesta |
|---|---|
| ¿Cuánto cuesta el plan Pro y qué incluye? | 29 USD/mes: 20 usuarios, 50 GB, soporte email 24/7, chat en vivo, 5 buzones, informes avanzados y automatizaciones. *(fuentes: base_conocimiento.pdf, planes_precios.json, terminos_de_uso.md)* |
| ¿Cuál es la política de reembolso? | Reembolso completo dentro de los primeros 30 días del primer pago, solicitándolo a facturacion@novadesk.example. *(fuentes: faq_soporte.html, terminos_de_uso.md)* |
| **¿Cuál es la capital de Francia?** | **"No encuentro esa información en los documentos."** |

Ese último caso es deliberado y es el que se defiende en una entrevista: el
modelo *sabe* que la capital de Francia es París, pero el sistema está
construido para no responder desde el conocimiento general del modelo, solo
desde la documentación de la empresa. En un asistente corporativo, una respuesta
inventada con tono seguro es peor que ninguna respuesta: si el agente
"improvisa" una política de reembolso que no existe, la empresa tiene un
problema legal, no un bug.

---

## 2. Cómo funciona (arquitectura)

AgentUP implementa un patrón **RAG** (*Retrieval-Augmented Generation*):
en lugar de reentrenar un modelo con los documentos de la empresa —caro, lento y
difícil de actualizar—, se recuperan los fragmentos relevantes en el momento de
la consulta y se le entregan al modelo como contexto acotado.

El sistema está partido en dos fases deliberadamente independientes:

```
      INGESTA (offline)                       SERVICIO (online)
data/ (pdf, md, csv, json, html)       Usuario → GET /  (chat UI)
   │  loaders por extensión                     POST /ask {"question"}
   ▼                                               │
chunks (1000 chars, solape 200)                    ▼
   │  embeddings Gemini                 FAISS retriever (top-4 chunks)
   ▼   (gemini-embedding-001)                      │
índice FAISS → vectorstore/  ───────►  prompt con contexto → Gemini
                                        (gemini-3.6-flash)
                                                   │
                                                   ▼
                                     {"answer": ..., "sources": [...]}
```

**Fase 1 — Ingesta (`src/ingest.py`).** Recorre la carpeta de documentos y
selecciona un *loader* distinto según la extensión: PyPDF para PDF, TextLoader
para Markdown, CSVLoader para tabulares (una fila = un documento), BSHTMLLoader
para HTML y un cargador propio para JSON. El texto resultante se trocea en
fragmentos de ~1000 caracteres con 200 de solape, se convierte a vectores con
los embeddings de Gemini y se persiste como índice FAISS en disco.

**Fase 2 — Servicio (`src/app.py` + `src/rag_chain.py`).** Una API en FastAPI
que al arrancar valida la API key, carga el índice y monta la cadena RAG. Ante
una pregunta: se vectoriza, FAISS devuelve los 4 fragmentos más cercanos, se
construye un prompt que instruye al modelo a responder *exclusivamente* con ese
contexto, Gemini redacta, y se devuelve un JSON con la respuesta y las fuentes
deduplicadas (incluyendo número de página cuando el origen es un PDF). La API
expone `POST /ask`, `GET /health` y sirve una interfaz de chat mínima en
`GET /`.

### Decisiones de arquitectura y su porqué

Esta sección es la más valiosa para una entrevista: cada elección tiene un
motivo defendible, no es la opción por defecto.

**Separar ingesta de servicio.** El índice se construye una sola vez y viaja
*dentro* de la imagen Docker. La consecuencia es que el servicio en producción
**no depende de ninguna base de datos externa**: arranca, lee un archivo local y
está listo. Cero infraestructura que mantener, cero coste de base de datos
vectorial, cero latencia de red en la búsqueda. El coste de esta decisión es que
actualizar la documentación requiere reconstruir el índice y redesplegar — una
compensación correcta para un corpus que cambia mensualmente, no cada hora.

**FAISS local en lugar de Pinecone / Weaviate / pgvector.** Para un corpus de
este tamaño, un índice en memoria resuelve la búsqueda en milisegundos sin
introducir un servicio más en la arquitectura. La regla aplicada fue elegir la
solución más simple que cumpla el requisito, y documentar cuándo dejaría de
servir (cuando el corpus deje de caber cómodamente en memoria o se necesite
actualización en caliente).

**El control de alucinaciones vive en el prompt, no en post-proceso.** El
*system prompt* obliga al modelo a devolver una frase exacta cuando el contexto
no contiene la respuesta. Es más robusto y más barato que intentar detectar
alucinaciones después de generarlas.

**Chunking de 1000 caracteres con solape de 200.** El solape existe para que una
frase que quede partida entre dos fragmentos siga siendo recuperable desde
cualquiera de los dos. Sin solape, la información justo en la frontera del corte
se vuelve prácticamente invisible para el retriever.

**Diseño testeable por inyección de dependencias.** La función `create_app()`
acepta opcionalmente la función que responde preguntas. En producción se
construye la real (que llama a Gemini); en los tests se inyecta una simulada.
Gracias a eso, **la suite completa corre sin gastar un solo token de API ni
requerir conexión a internet** — se puede ejecutar en CI, en un avión y sin
credenciales.

**Deploy en GCP Cloud Run en lugar de Oracle Cloud.** El challenge sugería OCI;
se optó por Cloud Run por disponibilidad de cuenta free tier, y **la desviación
se documentó explícitamente en el README** junto con el argumento de que, al
estar containerizado, el mismo `Dockerfile` se despliega en OCI sin tocar una
línea de código. Documentar una desviación con su justificación técnica vale
más que ocultarla.

### Stack

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Orquestación LLM | LangChain |
| Modelo de lenguaje | Google Gemini (`gemini-3.6-flash`) |
| Embeddings | `gemini-embedding-001` |
| Base vectorial | FAISS (local, persistido) |
| Backend | FastAPI + Uvicorn |
| Frontend | HTML + JavaScript vanilla |
| Parsers | PyPDF, BeautifulSoup, CSVLoader |
| Contenedor | Docker (`python:3.12-slim`) |
| Cloud | Google Cloud Run + Cloud Build |
| Testing | pytest + httpx |

---

## 3. Proceso de desarrollo

El proyecto no se escribió de corrido. Siguió una secuencia deliberada de
**diseño → plan → implementación incremental → verificación → deploy →
documentación**, y el historial de commits refleja exactamente ese orden.

**Primero el diseño, antes de una sola línea de código.** El primer commit del
repositorio no es código: es un documento de diseño que fija el caso de uso, los
formatos a soportar, el stack, la estrategia de deploy, el manejo de errores, la
estrategia de testing y —esto es lo importante— **una sección explícita de
"fuera de alcance"**. Ahí quedaron descartados por escrito la autenticación, la
subida dinámica de documentos, los formatos Office, el historial persistente y
el streaming de tokens. Decidir de antemano qué *no* se va a construir es lo que
permitió cerrar el proyecto en dos días en lugar de que se dilatara
indefinidamente.

El diseño también registró un **riesgo aceptado conscientemente**: desplegar en
GCP y no en OCI, con su mitigación documentada.

**Implementación incremental y verificable.** El trabajo se descompuso en 10
tareas, cada una cerrada con su propia revisión de código antes de pasar a la
siguiente. Cada commit deja el repositorio en un estado coherente: primero los
documentos ficticios, luego la carga multi-formato, luego el chunking y el
índice, luego la cadena RAG, luego la API, luego el contenedor, luego el deploy,
y al final la documentación. Los hallazgos menores que no justificaban bloquear
el avance (usar `html.parser` en lugar de `lxml`, ausencia de usuario no-root en
el Dockerfile) se registraron como deuda técnica consciente en lugar de
ignorarse en silencio.

**El choque con la realidad.** La verificación end-to-end contra la API real fue
el momento más instructivo del proyecto, porque rompió dos supuestos del diseño:

1. El modelo de embeddings elegido en el diseño (`text-embedding-004`) **había
   sido retirado** por el proveedor. Hubo que migrar a `gemini-embedding-001` y
   reconstruir el índice completo.
2. El modelo de lenguaje elegido (`gemini-2.0-flash`) **no tenía cuota
   disponible en el tier gratuito**. Al migrar a `gemini-3.6-flash` apareció un
   segundo problema encadenado: el nuevo modelo devuelve el contenido en
   bloques múltiples en lugar de una cadena de texto plano, lo que rompía la
   extracción de la respuesta. Se resolvió con una función de normalización que
   acepta ambos formatos.

Ambos fallos son de la misma familia y son la lección más transferible del
proyecto: **el ecosistema de modelos se mueve más rápido que la documentación**,
y por eso los tests unitarios no bastan — hace falta una verificación real
contra la API antes de dar nada por terminado. Los dos problemas se detectaron
antes del deploy, no después, precisamente porque la verificación end-to-end era
un paso planificado y no un extra opcional.

**Deploy y el problema que no era de código.** El primer `gcloud run deploy`
falló, y no por el código: en proyectos GCP nuevos, la service account de
Compute carece por defecto de los roles `cloudbuild.builds.builder` y
`storage.objectViewer` necesarios para que Cloud Build construya la imagen. Se
diagnosticó, se corrigió y **se documentó en el README como nota de IAM**, para
que la siguiente persona que clone el repositorio no pierda el mismo tiempo.

**Documentación como entregable, no como epílogo.** El README final incluye
diagrama de arquitectura, tabla de preguntas y respuestas reales, instrucciones
de ejecución local, instrucciones de deploy, la nota de IAM, evidencia visual
del servicio corriendo en Cloud Run y la justificación de haber usado GCP en
lugar de OCI.

---

## 4. Métricas

### 4.1. Métricas técnicas del proyecto (verificables)

| Métrica | Valor |
|---|---|
| Formatos de documento soportados | 5 (PDF, Markdown, CSV, JSON, HTML) |
| Líneas de código (src + tests + scripts + UI) | ~570 |
| Tests unitarios | 19, sin ninguna llamada a APIs externas |
| Commits | 15, incrementales y con estado coherente |
| Tareas planificadas y cerradas con revisión | 10 |
| Tamaño de chunk / solape | 1000 / 200 caracteres |
| Fragmentos recuperados por consulta | top-4 |
| Endpoints expuestos | 3 (`POST /ask`, `GET /health`, `GET /`) |
| Dependencias de infraestructura en runtime | 0 bases de datos externas |
| Tiempo de desarrollo end-to-end | ~2 días |
| Incidencias de integración detectadas antes de producción | 2 (modelos retirados / sin cuota) |
| Estado | Desplegado y accesible públicamente |

### 4.2. Impacto de negocio proyectado

> **Nota metodológica importante.** Las cifras de esta sección son
> **estimaciones y proyecciones** sobre el impacto que un sistema como AgentUP
> tendría al implantarse en una organización real. NovaDesk es una empresa
> ficticia creada para el challenge, de modo que **no son resultados medidos en
> producción**. Se incluyen porque describen correctamente la clase de problema
> que el proyecto resuelve y el orden de magnitud del retorno esperable; al
> usarlas en el CV o el portafolio conviene mantener el marco condicional
> ("permitiría", "está diseñado para reducir") y nunca presentarlas como datos
> observados. Un entrevistador que detecta una métrica inventada descarta el
> resto del proyecto.

**Reducción de consultas repetitivas de nivel 1.** En una mesa de ayuda o un
equipo interno, una fracción alta de las preguntas recibidas son repetidas y ya
están respondidas en algún documento: precios, límites por plan, integraciones
disponibles, políticas de reembolso, condiciones de uso. El objetivo de diseño
de AgentUP es **absorber ese tramo de consultas sin intervención humana**,
liberando al equipo para los casos que sí requieren criterio. Métrica de
seguimiento: porcentaje de consultas resueltas por el agente sin escalar a una
persona (*deflection rate*).

**Tiempo de respuesta: de minutos u horas a segundos.** El flujo actual sin
agente es: preguntar en un canal → esperar a que alguien con el contexto esté
disponible → recibir la respuesta. El flujo con agente es una consulta
respondida en segundos, disponible 24/7 y sin depender de que la persona que
sabe esté conectada. Métrica de seguimiento: tiempo medio hasta la primera
respuesta útil.

**Doble ahorro por consulta.** Cada pregunta desviada al agente ahorra tiempo
dos veces: el de quien pregunta (que deja de esperar) y el de quien
respondía (que deja de ser interrumpido). El segundo suele ser el más caro,
porque la interrupción no cuesta solo los minutos de responder, sino la
recuperación del contexto de la tarea que se estaba haciendo. Métrica de
seguimiento: número de interrupciones evitadas por semana en el equipo de
soporte o producto.

**Aceleración del onboarding.** Una persona recién incorporada no sabe qué
documento contiene qué. Un agente conversacional sobre la documentación interna
elimina esa barrera desde el primer día: en vez de aprender el mapa de archivos
de la empresa, se pregunta directamente. Métrica de seguimiento: tiempo hasta
autonomía de una persona nueva.

**Reducción del riesgo de información incorrecta.** Esta es la métrica menos
obvia y probablemente la más valiosa. Un asistente que inventa políticas
comerciales o legales genera compromisos que la empresa no puede sostener. La
combinación de respuesta acotada al corpus, citación explícita de fuentes y
negativa explícita ante lo desconocido está diseñada para que **el número de
respuestas no respaldadas por un documento sea cero**, y para que cualquier
respuesta pueda ser auditada hasta su origen. Métrica de seguimiento:
porcentaje de respuestas con fuente verificable.

**Coste de operación marginal.** La arquitectura no requiere base de datos
vectorial gestionada ni servidor permanente: se usa el tier gratuito del modelo
y Cloud Run, que escala a cero cuando no hay tráfico. Para un piloto interno,
esto significa que el coste de infraestructura es prácticamente nulo y toda la
inversión es el desarrollo inicial.

**Escalabilidad del enfoque.** Añadir un nuevo formato de documento es añadir un
*loader*; añadir documentación nueva es dejarla en la carpeta y reconstruir el
índice. El sistema no está atado al dominio de mesa de ayuda: el mismo diseño
sirve para documentación legal, manuales técnicos, procedimientos internos o
políticas de RR. HH. cambiando únicamente el corpus.

---

## 5. Modalidad de desarrollo

**Desarrollo individual, 100%.**

El proyecto fue realizado íntegramente por **Mathias Torres** de principio a
fin, sin equipo ni colaboradores. El historial de Git lo refleja: los 15 commits
del repositorio corresponden a un único autor.

Esto implica haber asumido personalmente todos los roles del ciclo de vida:

- **Análisis y diseño de solución** — definición del caso de uso, elección del
  patrón arquitectónico (RAG), selección del stack, delimitación explícita del
  alcance y registro de riesgos aceptados.
- **Ingeniería de datos** — generación del corpus documental ficticio en cinco
  formatos, coherente entre sí para que las respuestas fueran verificables, e
  implementación del pipeline de ingesta y vectorización.
- **Desarrollo backend** — API en FastAPI, cadena RAG, manejo de errores
  (400 en pregunta vacía, 502 ante fallo del modelo sin filtrar stack traces,
  fallo explícito al arranque si falta la API key).
- **Ingeniería de prompts** — diseño del *system prompt* de control de
  alucinaciones y del formato de citación de fuentes.
- **Frontend** — interfaz de chat en HTML y JavaScript vanilla.
- **QA y testing** — suite de 19 tests unitarios con dependencias inyectadas
  para correr sin APIs externas, más verificación manual end-to-end contra la
  API real antes del deploy.
- **DevOps / Cloud** — containerización con Docker, despliegue en Google Cloud
  Run vía Cloud Build, configuración de variables de entorno y diagnóstico y
  resolución de los permisos IAM del proyecto.
- **Documentación técnica** — documento de diseño, plan de implementación y
  README completo con arquitectura, ejemplos, guías de ejecución y deploy, y
  evidencia del servicio en producción.

---

## 6. Qué demuestra este proyecto

Resumido, para tenerlo presente al redactar el CV o al defenderlo en una
entrevista:

- **Capacidad de llevar un sistema de IA de la idea a producción accesible
  públicamente**, no un notebook ni una demo local.
- **Comprensión real del patrón RAG** y de sus componentes por separado:
  chunking, embeddings, búsqueda vectorial, construcción de contexto e ingeniería
  de prompts.
- **Criterio de arquitectura**: elegir la solución más simple que cumple el
  requisito y saber articular cuándo dejaría de servir.
- **Conciencia de que en IA aplicada la confiabilidad importa más que la
  fluidez**: trazabilidad de fuentes y negativa explícita ante lo desconocido
  como decisiones de diseño, no como añadidos.
- **Práctica de ingeniería sólida**: diseño previo, alcance acotado por escrito,
  commits incrementales, código testeable por inyección de dependencias,
  documentación de deuda técnica y de desviaciones.
- **Autonomía completa en el ciclo de vida**, incluyendo la parte que no es
  código: containerización, cloud, IAM y documentación.
- **Capacidad de diagnóstico bajo cambio externo**: dos modelos del proveedor
  dejaron de estar disponibles a mitad del proyecto y se resolvió sin
  replantear la arquitectura.

---

## 7. Enlaces

- **Repositorio:** https://github.com/MathiasTL/AgentUP
- **Demo en vivo:** https://agentup-382104851468.us-central1.run.app
- **Contexto:** challenge final del programa de Alura
