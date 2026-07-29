# ProfAI — Tutor de IA multiagente para aprender Prompt Engineering

> Documento de referencia para CV y portafolio web.
> Proyecto desarrollado en un hackathon de ~48 horas (9–10 de agosto de 2025).
> Repositorio: `NickSalA/Hackaton-06-2025` · Stack: Next.js 15 · React 19 · Flask · LangGraph · Azure OpenAI · Azure AI Search · PostgreSQL

---

## 1. De qué trata ProfAI

ProfAI es una **plataforma de aprendizaje conversacional** que sustituye el material estático de un curso por un profesor de IA que conversa, se adapta y evalúa. El dominio elegido fue **Prompt Engineering**: una disciplina que cambia tan rápido que los cursos grabados quedan obsoletos antes de publicarse, y donde el aprendizaje real ocurre practicando y recibiendo retroalimentación, no leyendo diapositivas.

El problema de fondo es conocido: en la formación autodirigida, la mayoría de los estudiantes abandona en las primeras lecciones. No es falta de contenido —hay más material gratuito del que nadie puede consumir— sino falta de **acompañamiento**: nadie responde tus dudas en el momento exacto en que aparecen, nadie detecta que avanzaste sin entender, y nadie ajusta el ritmo a tu nivel.

ProfAI ataca ese vacío con tres decisiones de diseño:

**Un tutor que responde con fuentes reales, no con alucinaciones.** Todo lo que el chatbot afirma se apoya en una base de conocimiento propia construida a partir de documentación curada de prompt engineering, indexada en Azure AI Search y recuperada vía RAG en cada turno de la conversación. El estudiante pregunta en lenguaje natural; el sistema recupera los fragmentos relevantes y responde sobre esa evidencia.

**Un sistema multiagente, no un único prompt gigante.** En lugar de un solo modelo intentando hacerlo todo, ProfAI orquesta **8 agentes especializados** sobre un grafo de LangGraph. Cada uno tiene una responsabilidad acotada y verificable: uno filtra mensajes inválidos antes de gastar tokens, otro clasifica la intención del usuario, otro conversa con la base de conocimiento, otro decide si el estudiante ya está listo para evaluarse, otro genera el cuestionario. Esta separación hace que el comportamiento sea depurable —cuando algo falla, se sabe qué agente falló— y que cada pieza se pueda mejorar sin romper el resto.

**Evaluación que emerge de la conversación.** ProfAI no pone un examen al terminar la lección: un agente de evaluación monitorea el diálogo y determina cuándo el estudiante demuestra comprensión suficiente. Solo entonces se dispara el agente de cuestionario, que genera preguntas (opción múltiple, verdadero/falso, abiertas) sobre lo efectivamente conversado. La evaluación deja de ser un trámite final y pasa a ser un chequeo oportuno.

Alrededor de eso se construyó una plataforma completa: autenticación con NextAuth, un panel con **13 lecciones** desbloqueables secuencialmente, historial de chat persistente por lección, panel lateral de apoyo en Markdown, seguimiento de progreso y racha diaria de estudio, y registro de accesos para analítica.

---

## 2. Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│  FRONTEND — Next.js 15 (App Router) + React 19 + Tailwind 4  │
│  Landing · Login · Panel · Lecciones · Chat                  │
└───────────────┬──────────────────────────────────────────────┘
                │  7 API Routes (BFF)
┌───────────────▼──────────────────────────────────────────────┐
│  CAPA DE DATOS — Prisma 6 + PostgreSQL                       │
│  Usuarios · Sesiones · Chats · Mensajes · Progreso · Accesos │
└───────────────┬──────────────────────────────────────────────┘
                │  HTTP (JSON)
┌───────────────▼──────────────────────────────────────────────┐
│  BACKEND IA — Flask + LangGraph                              │
│                                                              │
│   Contexto → Supervisión ─┬─→ Chatbot (RAG) → Evaluación     │
│                           │        ↓              ↓          │
│                           └─→ Resumen      Cuestionario      │
│                                    ↓                         │
│                        Análisis · Memoria a Largo Plazo      │
└───────────────┬──────────────────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────────────────┐
│  AZURE — OpenAI (GPT) · AI Search (RAG) ·                    │
│          Document Intelligence (OCR) · Speech (voz)          │
└──────────────────────────────────────────────────────────────┘
```

### Los 8 agentes

| Agente | Responsabilidad |
|---|---|
| **Contexto** | Valida que el mensaje sea legítimo (idioma reconocible, sin insultos, no sea texto aleatorio) antes de invocar al modelo principal. Actúa como filtro de coste y de abuso. |
| **Supervisión** | Clasifica la intención: ¿el usuario quiere conversar o pide un resumen de lo hablado? Enruta el grafo en consecuencia. |
| **Chatbot** | Núcleo conversacional con RAG sobre Azure AI Search y memoria de conversación. Incluye fallback a chat sin base de conocimiento si el retriever falla. |
| **Análisis** | Extrae información estructurada (JSON) de los mensajes del usuario. |
| **Resumen** | Reconstruye la conversación previa en tono empático: primera pregunta, respuesta dada, temas tratados. |
| **Memoria a Largo Plazo** | Detecta datos persistentes del estudiante y los almacena para personalizar sesiones futuras. |
| **Evaluación** | Determina si el estudiante está listo para el cuestionario (`{listo, motivo}`), a partir de la última respuesta del tutor y el historial. |
| **Cuestionario** | Genera ítems objetivos de verificación de comprensión en JSON estricto, con parseo defensivo ante respuestas malformadas del modelo. |

### Modelo de datos (Prisma / PostgreSQL)

11 modelos: `User`, `Account`, `Session` (Auth.js) · `Course`, `Lesson` (con `infoPanel` y `chatWelcomeMessage` configurables desde BD) · `ChatSession`, `Message` (historial persistente con roles) · `Progress` (estado y racha) · `AccessLog` (analítica de uso), con índices compuestos en las rutas de consulta calientes (`[userId, createdAt]`, `[chatSessionId, createdAt]`).

---

## 3. Mi rol en el proyecto

**Desarrollo grupal.** Equipo de 3 personas trabajando en paralelo durante el hackathon, con integración continua sobre `main`.

| Integrante | Foco |
|---|---|
| Compañero A | Backend de IA: flujo LangGraph y agentes de evaluación/cuestionario |
| Compañero B | Frontend de producto: panel, componentes de lecciones y chat |
| **Mathias Torres (yo)** | **Liderazgo e integración · Dataset y base de conocimiento (RAG) · Frontend de entrada** |

### Lo que hice

**Liderazgo técnico e integración.** Definí cómo se conectaban las tres piezas del sistema —frontend Next.js, capa de datos Prisma y backend Flask— y sostuve la integración entre ramas durante las 48 horas. En un hackathon con tres personas commiteando en paralelo sobre el mismo repositorio, el trabajo de integración es el que determina si al final hay una demo o tres módulos que no se hablan entre sí. Coordiné el contrato de la API entre el BFF de Next.js y el servicio Flask, y resolví los conflictos de merge que surgieron de la convergencia de ramas.

**Construcción del dataset de Prompt Engineering.** Diseñé y curé el corpus que da autoridad al tutor: la selección de fuentes, la estructura temática en **13 lecciones progresivas** (fundamentos, historia y evolución, elementos de un prompt, técnicas de optimización, patrones básicos y avanzados, ingeniería de contexto, ingeniería de instrucciones, salida estructurada, entre otras) y la preparación del material documental que alimenta la base de conocimiento. Esta es la diferencia entre un chatbot genérico y un tutor que enseña un temario coherente: sin un corpus bien estructurado, el RAG recupera ruido.

**Ingesta de PDFs en Azure AI Search.** Implementé y operé el pipeline que convierte documentos en conocimiento consultable:

1. **Extracción** — cada PDF pasa por Azure Document Intelligence (modelo `prebuilt-read`) para OCR y lectura estructurada página por página.
2. **Chunking** — el texto se segmenta en fragmentos de 1 000 caracteres con 100 de solapamiento, preservando continuidad semántica entre cortes.
3. **Indexación** — cada chunk recibe un UUID y se carga al índice `fundamentos` de Azure AI Search vía `SearchClient`.
4. **Sincronización continua** — un proceso de watch monitorea la carpeta de origen, procesa archivos nuevos sin reprocesar los ya ingeridos, y aísla en una carpeta de errores cualquier documento que falle, para que un PDF corrupto no detenga el pipeline completo.

El resultado es que subir un PDF nuevo al corpus no requiere tocar código: se deja el archivo en la carpeta y queda consultable por el tutor en segundos.

**Frontend de entrada.** Desarrollé la landing page y la pantalla de login —la primera impresión del producto en la demo— además de ajustes en la navegación y la identidad visual.

---

## 4. Métricas

### 4.1 Métricas técnicas verificables

| Métrica | Valor |
|---|---|
| Duración del desarrollo | ~48 horas (hackathon) |
| Tamaño del equipo | 3 desarrolladores |
| Commits totales | 59 |
| Backend Python | ~1 515 líneas |
| Frontend TypeScript / TSX | ~1 752 líneas |
| Agentes de IA especializados | 8 |
| Modelos de datos en PostgreSQL | 11 |
| API Routes en Next.js | 7 |
| Lecciones estructuradas del curso | 13 |
| Servicios de Azure integrados | 4 (OpenAI, AI Search, Document Intelligence, Speech) |
| Tamaño de chunk / solapamiento en el RAG | 1 000 / 100 caracteres |
| Modalidades de entrada soportadas | Texto y voz (Web Speech API + Azure Speech) |

### 4.2 KPIs de impacto — objetivos a validar

> ⚠️ **Nota de honestidad:** las cifras de esta sección son **hipótesis de producto y objetivos de medición**, no resultados medidos. ProfAI es un prototipo de hackathon sin despliegue en producción ni datos de uso real. Se documentan porque definen qué habría que instrumentar para demostrar valor, y porque el esquema de base de datos (`Progress`, `AccessLog`, `Message`) ya fue diseñado para capturarlas.

**Sobre el aprendizaje**

| KPI | Cómo se mide | Objetivo hipotético |
|---|---|---|
| Tasa de finalización del curso | `Progress.status = COMPLETED` / usuarios inscritos | Elevarla frente a la línea base de cursos autodirigidos, notoriamente baja |
| Tiempo hasta resolver una duda | Timestamp pregunta → primera respuesta útil | Segundos, frente a las horas o días de un foro |
| Retención semanal | Racha de días activos en `Progress` | Sostener la racha más allá de la primera semana |
| Aprobación en el primer intento del cuestionario | Resultados del Agente de Cuestionario | Alta, como señal de que la evaluación se dispara en el momento correcto |
| Profundidad de la conversación | Mensajes por sesión en `Message` | Más turnos = mayor exploración activa del tema |

**Sobre la operación**

| KPI | Cómo se mide | Objetivo hipotético |
|---|---|---|
| Coste por conversación | Tokens facturados / sesiones | Reducirlo vía el Agente de Contexto, que descarta mensajes inválidos antes de invocar el modelo caro |
| Tasa de respuestas sin fundamento | Auditoría de respuestas sin cita del corpus | Minimizarla; es la métrica que justifica la arquitectura RAG |
| Tiempo de incorporación de contenido nuevo | Desde el PDF hasta que el tutor responde sobre él | Minutos, gracias al pipeline de sincronización automática |
| Ratio estudiantes por instructor humano | Estudiantes atendidos sin intervención humana | El argumento de escalabilidad del producto |

**Cómo instrumentarlo.** La medición no requiere rediseñar el sistema: `AccessLog` ya registra accesos por usuario y curso, `Progress` ya modela estado y racha, y `Message` ya almacena cada turno con rol, timestamp y un campo `meta` en JSON pensado para adjuntar telemetría (tokens consumidos, chunks recuperados, latencia). El siguiente paso natural del proyecto es un dashboard de analítica sobre esas tablas.

---

## 5. Decisiones de diseño destacables

**Separación de agentes en lugar de un prompt monolítico.** Un único prompt con todas las instrucciones es imposible de depurar y degrada al crecer. Ocho agentes con contratos JSON explícitos permiten aislar fallos, testear cada pieza por separado y usar modelos distintos según el coste que justifique cada tarea.

**El filtro barato antes del modelo caro.** El Agente de Contexto rechaza mensajes sin sentido, ofensivos o en idiomas no soportados antes de que lleguen al modelo principal. Es una decisión de coste, de seguridad y de calidad de datos a la vez.

**Parseo defensivo de las salidas del LLM.** Los agentes que producen JSON (Evaluación, Cuestionario, Análisis) limpian delimitadores de código y aplican deserialización con fallback. Los modelos incumplen el formato con más frecuencia de la que uno querría; el sistema no debe caerse por eso.

**Contenido configurable desde base de datos.** El mensaje de bienvenida y el panel informativo de cada lección viven en `Lesson.chatWelcomeMessage` e `infoPanel`, no en el código. Editar el curso no requiere desplegar.

**Pipeline de ingesta idempotente y tolerante a fallos.** Los archivos ya procesados no se reprocesan y los documentos problemáticos se aíslan en cuarentena en lugar de abortar la sincronización.

---

## 6. Stack técnico

**Frontend** — Next.js 15 (App Router, Turbopack) · React 19 · TypeScript · TailwindCSS 4 · React Markdown · NextAuth v4

**Backend** — Python · Flask · Flask-CORS · LangGraph · LangChain · Gunicorn

**IA / Datos** — Azure OpenAI (`AzureChatOpenAI`) · Azure AI Search (RAG) · Azure Document Intelligence (OCR) · Azure Cognitive Services Speech (TTS/STT) · Web Speech API

**Persistencia** — PostgreSQL · Prisma 6 · Prisma Adapter para Auth.js

**Herramientas** — Git · GitHub · ESLint · pytest

---

## 7. Versiones cortas para CV

**Formato una línea**

> **ProfAI — Tutor de IA multiagente (Hackathon, 48 h, equipo de 3).** Lideré la integración del sistema y construí el pipeline RAG completo: curación del dataset de Prompt Engineering (13 lecciones), OCR de PDFs con Azure Document Intelligence, chunking e indexación en Azure AI Search. Stack: Next.js 15, Flask, LangGraph (8 agentes), Azure OpenAI, PostgreSQL.

**Formato viñetas**

- Lideré la integración técnica de una plataforma educativa con IA desarrollada por un equipo de 3 personas en 48 horas, articulando frontend Next.js 15, capa de datos Prisma/PostgreSQL y backend Flask con LangGraph.
- Diseñé y curé el dataset de Prompt Engineering que da soporte al tutor, estructurado en 13 lecciones progresivas.
- Implementé el pipeline de ingesta RAG end-to-end: extracción OCR con Azure Document Intelligence, chunking con solapamiento e indexación automática en Azure AI Search, con sincronización continua idempotente y cuarentena de errores.
- Desarrollé la landing page y el flujo de autenticación del producto.

**Formato portafolio (párrafo)**

> ProfAI nació de una pregunta simple: ¿por qué la mayoría de la gente abandona los cursos online? Nuestra respuesta fue que el problema no es el contenido, es la ausencia de un profesor que responda cuando surge la duda. Construimos un tutor de IA sobre 8 agentes especializados orquestados con LangGraph, capaz de conversar apoyándose en un corpus curado de Prompt Engineering, detectar cuándo el estudiante ya entendió y evaluarlo en ese momento exacto. Mi trabajo fue liderar la integración del sistema y construir la base de conocimiento que le da autoridad: desde la curación del dataset hasta el pipeline que convierte PDFs en conocimiento consultable en segundos.

---

## 8. Qué haría diferente con más tiempo

Un hackathon de 48 horas obliga a decidir qué no se hace. Los límites reconocidos del prototipo:

- **Sin cobertura de tests.** `pytest` está en las dependencias, pero no hubo tiempo de escribir la suite. Sería lo primero en abordar.
- **Estado del chatbot en memoria del proceso.** El `InMemorySaver` de LangGraph no sobrevive a reinicios ni escala horizontalmente; migrarlo a un checkpointer persistente es requisito para producción.
- **Instancia única del chatbot compartida entre usuarios.** Funciona para una demo, no para uso concurrente real.
- **Sin telemetría instrumentada.** Los KPIs de la sección 4.2 están diseñados pero no capturados. El campo `meta` en `Message` está listo para recibirlos.
- **Base de conocimiento única.** El sistema apunta al índice `fundamentos`; escalar a un índice por lección permitiría recuperación más precisa por tema.
