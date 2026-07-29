# Eissential — Documento fuente para CV y portafolio

> **Uso de este archivo:** es un documento fuente, no un texto final. Contiene la narrativa completa del proyecto, el detalle técnico, las métricas y —al final— bloques ya recortados para pegar directamente en el CV, en LinkedIn o en la web de portafolio.

**Proyecto:** Eissential
**Rol:** Desarrollador full-stack, diseñador de producto y responsable de la arquitectura (proyecto individual)
**Periodo:** mayo 2026 — en desarrollo activo
**Stack:** Next.js 16 · React 19 · TypeScript · Tailwind CSS v4 · shadcn/ui (Radix) · Supabase (Postgres + Auth) · Recharts · Vercel
**Repositorio:** proyecto propio, desplegado en Vercel con integración continua desde `main`

---

## 1. Qué es Eissential

Eissential es una aplicación web de productividad personal que unifica, en un único flujo guiado, tres metodologías que normalmente se usan por separado y de forma desconectada:

1. **SMART** — para definir objetivos bien formulados *antes* de empezar a trabajar.
2. **Matriz de Eisenhower** — para priorizar tareas según el eje urgencia × importancia.
3. **Kanban** — para ejecutar y seguir el progreso de aquello que realmente se priorizó.

El nombre fusiona *Eisenhower* + *essential*, y encapsula la tesis del producto: **lo esencial es lo importante, no solo lo urgente**.

### El problema que ataca

La mayoría de gestores de tareas empiezan por la caja de entrada: se anota todo lo que aparece y se trabaja sobre lo que grita más fuerte. El resultado es conocido —listas que crecen sin control, ejecución reactiva, y objetivos de fondo que nunca avanzan porque siempre hay algo urgente encima.

Las personas que gestionan proyectos personales o pequeños caen sistemáticamente en tres patrones:

- Acumulan tareas sin un objetivo claro que las justifique.
- Trabajan sobre lo urgente y descuidan lo importante.
- Pierden de vista los plazos hasta que ya es tarde.

### La decisión de producto que lo diferencia

Eissential **impone una disciplina previa: no se pueden crear tareas hasta haber definido un objetivo SMART completo.** Esa restricción —deliberadamente incómoda— es el corazón del producto. Fuerza claridad de propósito antes de la ejecución y convierte al Kanban en la consecuencia de una priorización consciente, no de la urgencia del momento.

El flujo es opinado y secuencial:

```
Objetivo SMART  →  Backlog  →  Matriz Eisenhower  →  Kanban  →  Hecho
   (5 pasos)                    (urgencia × importancia)   (todo→curso→done)
```

Y está reforzado por reglas de negocio explícitas, no por buenas intenciones:

- Un proyecto debe completar los **5 pasos SMART** antes de poder recibir tareas. Intentar crear una tarea sin ello está bloqueado en la UI, con un CTA que redirige al flujo correcto.
- Toda tarea nace en el **backlog** y solo sale de ahí al ser clasificada en un cuadrante de Eisenhower (asignando importancia y urgencia).
- **Solo el cuadrante "Hacer Primero"** (urgente + importante) puede promoverse al Kanban. Lo que no es importante no llega a ejecución: se planifica, se delega o se elimina.

### Usuario objetivo

*"El ejecutor con metas"*: estudiante avanzado, freelancer, emprendedor temprano o profesional individual que gestiona sus propios proyectos, conoce (o quiere adoptar) marcos como SMART y Eisenhower, y trabaja principalmente en desktop pero necesita consultar y mover tareas desde el móvil.

### Qué NO es (alcance deliberadamente acotado)

- No es un gestor colaborativo multiusuario — hoy es single-user por diseño.
- No es un reemplazo de Jira/Asana con dependencias, sprints y reporting avanzado.
- No es una bandeja de entrada libre: las tareas siempre cuelgan de un proyecto SMART completado.

Delimitar el "no" con esta precisión fue una decisión de producto tan importante como definir el "sí": mantuvo el alcance ejecutable en solitario y evitó construir features que diluyeran la tesis central.

---

## 2. El producto, módulo por módulo

### 2.1 Autenticación y protección de rutas
Registro e inicio de sesión con email + contraseña sobre **Supabase Auth**, con verificación por correo y redirección a un endpoint de callback. Un **middleware de Next.js** protege las rutas privadas (`/`, `/dashboard`, `/projects`, `/tasks`), redirige a login cuando no hay sesión y —a la inversa— saca a los usuarios autenticados de las páginas de auth. Validación de contraseña en cliente y página de éxito post-registro.

### 2.2 Proyectos SMART
El módulo donde vive la tesis del producto. La creación de un proyecto abre un **wizard en formato de timeline vertical de 5 pasos** (Specific, Measurable, Achievable, Relevant, Time-bound): el usuario completa uno a la vez y avanza, con los pasos ya cerrados colapsados a un check + título para no saturar la vista.

Cada proyecto muestra chips de progreso S-M-A-R-T y un **countdown en tiempo real** hasta la fecha límite. Un modal de detalle amplio presenta el objetivo en formato visual: la definición (S) destacada, tres columnas para M/A/R y un bloque temporal (T) con la cuenta regresiva.

### 2.3 Backlog + Matriz de Eisenhower
Vista combinada en una sola pantalla: panel de **backlog** a la izquierda como fuente de tareas, **matriz 2×2** a la derecha como destino. Se arrastran tareas del backlog al cuadrante correspondiente mediante **drag & drop nativo HTML5**, y al soltarlas se les asignan automáticamente los valores de importancia y urgencia.

Los cuatro cuadrantes tienen acciones distintas y coherentes con la metodología: *Hacer Primero* (único que promueve a Kanban, con acción masiva "enviar todas"), *Planificar*, *Delegar* y *Eliminar*.

### 2.4 Tablero Kanban
Tres columnas —Por Hacer / En Curso / Hechas— con drag & drop entre ellas en desktop y botones explícitos de "mover →" como alternativa accesible en móvil. Cada tarjeta muestra su proyecto de origen para no perder la trazabilidad con el objetivo SMART que la justifica.

### 2.5 Panel de control con analítica
Dashboard construido sobre **Recharts** con cuatro visualizaciones que responden a preguntas concretas del usuario:

| Gráfico | Pregunta que responde |
|---|---|
| Dona por cuadrante Eisenhower | ¿Estoy priorizando o solo apagando incendios? |
| Barras apiladas por proyecto | ¿Qué proyecto está estancado y cuál avanza? |
| Embudo del flujo (Backlog → Eisenhower → Kanban → Hechas) | ¿Dónde se atascan mis tareas? |
| Área temporal acumulada (30 días) | ¿Estoy manteniendo el ritmo de ejecución? |

Complementado con tarjetas-resumen clicables que actúan como atajos de navegación y un listado de proyectos recientes con su progreso SMART.

### 2.6 Observabilidad
Endpoint `GET /api/health` que verifica la conectividad real con la base de datos contando filas en las tablas principales — pensado para monitoreo externo y diagnóstico rápido de despliegues.

---

## 3. Arquitectura y decisiones técnicas

### Stack y estructura

```
app/          rutas (App Router): raíz con redirect por sesión, auth/*, dashboard/, api/health
components/   vistas por módulo (*-view.tsx) + dashboard/ (gráficos) + ui/ (shadcn)
lib/          app-context.tsx (estado global), data-access.ts, database.types.ts,
              dashboard-metrics.ts, project-status.ts, types.ts, supabase/
hooks/        use-mobile, use-toast
```

- **Framework:** Next.js 16 (App Router) + React 19
- **Lenguaje:** TypeScript 5.7, con tipado estricto del dominio
- **Estilos:** Tailwind CSS v4 + tokens de diseño propios; componentes shadcn/ui sobre Radix UI (accesibilidad garantizada por primitivos)
- **Datos y auth:** Supabase (Postgres + Auth) vía `@supabase/ssr`
- **Visualización:** Recharts sobre los tokens de color de marca (`--chart-1..5`), coherentes en tema claro y oscuro
- **Despliegue:** Vercel, auto-deploy en cada merge a `main`

### Decisiones de arquitectura que vale la pena defender

**1. Estado global vía React Context con actualizaciones optimistas.**
Toda mutación (crear proyecto, avanzar paso SMART, priorizar, mover en Kanban) actualiza primero el estado local y luego persiste en Supabase. Si la persistencia falla, se hace **rollback del estado y se notifica al usuario con un toast**. El resultado es una UI que responde de forma instantánea al drag & drop sin sacrificar la consistencia con el backend. Es el patrón correcto para una app single-user cuyo dataset completo cabe en memoria.

**2. Separación estricta entre derivación de datos y presentación.**
Toda la lógica analítica del dashboard vive en `lib/dashboard-metrics.ts` como **funciones puras sin React, sin hooks y sin estado**: reciben `(projects, tasks)` y devuelven el array listo para graficar. Los componentes de gráfico solo reciben props y renderizan, cada uno con su propio estado vacío. La vista contenedora calcula todo en un único `useMemo` y reparte.

El beneficio no es estético: aisló la parte propensa a errores (agregaciones, ventanas temporales, acumulados) en unidades testeables de forma independiente, y evitó que el componente de dashboard creciera hasta volverse inmantenible.

**3. Frontera explícita entre el modelo de dominio y el modelo de base de datos.**
El dominio usa camelCase y tipos semánticos (`Importance`, `Urgency`, `TaskLocation`, `KanbanStatus` como uniones literales); la base de datos usa snake_case. `lib/database.types.ts` centraliza los conversores en ambas direcciones. Ningún componente conoce la forma de la tabla, y un cambio de esquema tiene un único punto de impacto.

**4. Estado derivado, no almacenado.**
El estado visual de un proyecto (`wizard` / `activo` / `vencido` / `completado` / `vencido-completado`) **no se guarda en base de datos**: se deriva de sus campos mediante una función pura. Eso elimina de raíz toda una clase de bugs de desincronización — no existe forma de que un proyecto esté marcado "activo" en la tabla mientras su deadline ya venció.

**5. Navegación por estado en lugar de rutas.**
Dentro de `/dashboard`, el cambio entre vistas es estado local, no rutas separadas. Decisión consciente: el dataset ya está cargado completo en memoria, así que enrutar añadiría latencia y complejidad sin aportar nada al usuario.

### Modelo de datos

Dos tablas principales en Postgres, con `user_id` en ambas y aislamiento por Row Level Security:

- **`projects`** — un campo de texto por cada letra SMART, `current_step` (0–4), `completed`, `deadline`, `completed_at` y timestamps de auditoría.
- **`tasks`** — vinculada al proyecto por FK, con `importance`, `urgency`, `location` (la etapa del flujo), `kanban_status`, `position` para ordenamiento y `completed_at`.

El campo `completed_at` en tareas se añadió específicamente para habilitar la analítica temporal: sin marca de tiempo de completado no hay forma de graficar ritmo de ejecución.

---

## 4. Métricas

### 4.1 KPIs de producto — lo que Eissential está diseñado para optimizar

Estos son los indicadores objetivo del producto y la instrumentación con la que se medirían. Se declaran como **hipótesis de diseño con método de medición definido**, no como resultados observados: la app aún no ha corrido un ciclo de medición con usuarios.

| # | KPI | Hipótesis / meta | Cómo se mide con los datos que ya existen |
|---|---|---|---|
| 1 | **Ratio de trabajo importante** — % de tareas ejecutadas que estaban en el cuadrante "Hacer Primero" | ≥ 70 % del esfuerzo en tareas importantes (vs. la mezcla reactiva habitual) | Tareas con `kanban_status = done` cruzadas por su cuadrante de origen (`importance`/`urgency`) |
| 2 | **Tiempo de priorización** — minutos para clasificar un backlog completo | < 2 min para 20 tareas, gracias al drag & drop directo a cuadrante frente a formularios campo por campo | Delta entre `created_at` y el paso a `location = 'eisenhower'`, agregado por sesión |
| 3 | **Tasa de cumplimiento de plazos** — proyectos completados en fecha | ≥ 80 % de proyectos con `completed_at ≤ deadline` | Ya calculado por la función de estado: distingue `completado` de `vencido-completado` |
| 4 | **Tasa de abandono del backlog** — tareas que nunca llegan a priorizarse | < 15 %, forzada a la baja porque la matriz obliga a decidir (incluido "eliminar") | Tareas que permanecen en `location = 'backlog'` más de N días |
| 5 | **Densidad de propósito** — % de tareas que cuelgan de un objetivo SMART completo | **100 % por construcción** — es una invariante del modelo, no una aspiración | Garantizado por la regla de negocio; verificable con una sola consulta |
| 6 | **Cycle time** — días desde que una tarea entra al Kanban hasta que se completa | Reducción sostenida mes a mes, visible en el gráfico de acumulado | `completed_at` menos la fecha de promoción a `location = 'kanban'` |
| 7 | **Ritmo de ejecución (throughput)** — tareas completadas por semana | Tendencia creciente y estable, sin picos de fin de plazo | Gráfico de área acumulada de completadas, ya implementado |
| 8 | **Retención de flujo** — % de proyectos que llegan del paso SMART 0 al 4 | ≥ 60 % (el wizard es el punto natural de fricción y abandono) | Distribución de `current_step` sobre proyectos creados |

**Nota sobre el KPI 5:** es el más interesante de defender en una entrevista, porque no es una métrica que se optimiza — es una propiedad que el diseño del sistema hace imposible de violar. El resto de herramientas del mercado no pueden reportarlo en absoluto.

### 4.2 Métricas del desarrollo (datos reales del repositorio)

| Métrica | Valor |
|---|---|
| Líneas de TypeScript/TSX propias | ~4.200 (excluyendo los primitivos de shadcn/ui) |
| Archivos `.ts` / `.tsx` en el proyecto | 92 |
| Módulos funcionales completos | 6 (auth, proyectos SMART, backlog, Eisenhower, Kanban, dashboard analítico) |
| Vistas principales | 4, más flujo de autenticación completo |
| Gráficos de analítica | 4, con estados vacíos propios y soporte de tema claro/oscuro |
| Tablas de base de datos diseñadas | 2, con RLS por usuario |
| Commits | 32 |
| Pull requests integrados | 5, cada uno con feature branch propia |
| Ciclo de release más rápido | 5 ítems de roadmap P0 diseñados, implementados e integrados en un solo día |
| Documentos de producto/diseño escritos | 6 (1 PRD + 2 specs de diseño + 3 planes de implementación) |
| Duración del ciclo documentado | 16 → 30 de mayo de 2026 (desarrollo activo continuo) |

---

## 5. El desarrollo: qué hice, en orden

El proyecto se ejecutó en cuatro fases claramente diferenciadas, cada una con su propio criterio de "terminado".

### Fase 1 — Prototipo de interfaz y sistema de diseño *(16–18 de mayo)*

Objetivo: validar que las tres metodologías podían convivir en una misma interfaz sin sentirse como tres apps pegadas.

- Construcción de las cuatro vistas principales con datos en memoria, priorizando la validación del flujo por encima de la persistencia.
- Diseño de la **matriz de Eisenhower como cuadrícula 2×2** con ejes rotulados, jerarquía cromática por cuadrante y etiquetas de acción explícitas (*Hacer Primero / Planificar / Delegar / Eliminar*) en lugar de nombres técnicos.
- Implementación del **drag & drop nativo HTML5** para arrastrar tareas del backlog a los cuadrantes y entre columnas del Kanban — sin dependencias externas.
- Diseño del **wizard SMART como timeline vertical con colapso progresivo**: los pasos ya cerrados se reducen a check + título, manteniendo el foco en el paso activo sin perder el contexto de lo hecho.
- Definición del sistema de diseño: paleta con tokens semánticos, tipografía editorial (Libre Baskerville, IBM Plex Mono, Lora) y adaptación completa a shadcn/ui.
- Modal de detalle de proyecto con el objetivo SMART presentado en formato visual, no como formulario.
- Countdown de deadline en tiempo real, con corrección posterior del cálculo de zona horaria.

**Aprendizaje de la fase:** las etiquetas de acción en los cuadrantes fueron el cambio de mayor impacto por menor esfuerzo. La matriz de Eisenhower es inútil si el usuario tiene que recordar qué significa cada esquina.

### Fase 2 — Backend, persistencia y autenticación *(18–22 de mayo)*

Objetivo: convertir el prototipo en una aplicación real, multiusuario a nivel de aislamiento de datos.

- Diseño del **esquema de Postgres** en Supabase: tablas `projects` y `tasks`, tipos, claves foráneas y políticas de Row Level Security por `user_id`.
- Configuración de los tres clientes de Supabase requeridos por el App Router (navegador, servidor y middleware) mediante `@supabase/ssr`.
- **Sistema de autenticación completo**: registro con verificación por email, login, callback, logout y páginas de error y éxito.
- **Middleware de protección de rutas** con redirección bidireccional (usuarios sin sesión fuera de las rutas privadas; usuarios con sesión fuera de las páginas de auth).
- Implementación del patrón de **actualizaciones optimistas con rollback** en las ~14 operaciones de mutación de la aplicación, incluyendo manejo de errores y feedback vía toasts.
- Diseño de la **capa de conversión DB↔dominio** con tipos de insert y update derivados, para que ningún componente dependa de la forma de la tabla.
- Endpoint de health check para verificar conectividad con la base de datos en producción.

**Decisión relevante:** al conectar la persistencia, la app pasó de sentirse instantánea a sentirse lenta en cada arrastre. Las actualizaciones optimistas con rollback recuperaron la sensación del prototipo sin renunciar a la integridad de los datos — el drag & drop es el gesto central del producto y no podía tener latencia perceptible.

### Fase 3 — Producto: PRD, priorización y ejecución del roadmap P0 *(27 de mayo)*

Objetivo: dejar de construir por intuición y empezar a construir por prioridad.

- Auditoría completa del código existente y redacción de un **PRD de 12 secciones**: visión y propuesta de valor, problema y personas, principios de diseño, estado actual módulo por módulo, user journeys, arquitectura, modelo de datos, deuda técnica, roadmap por épicas, matriz de priorización, riesgos y apéndice técnico.
- Identificación explícita de **6 ítems de deuda técnica** —incluyendo un componente huérfano duplicado, una capa de acceso a datos sin consumir, una zona horaria hardcodeada y la ausencia de tests— documentados con su coste y su recomendación.
- Organización del backlog en **5 épicas** (UX, funcionalidad core, datos y métricas, colaboración, plataforma y calidad) y priorización de 18 ítems mediante una **matriz de impacto × esfuerzo** con niveles P0–P3.
- **Ejecución completa del bloque P0 en un solo ciclo**, con plan de implementación escrito previamente:
  - Sustitución del sidebar lateral por una **headbar superior con menú desplegable**, liberando el ancho completo de la pantalla para el contenido — la queja principal sobre la interfaz anterior.
  - Ampliación del modal de detalle de proyecto para dar espacio y jerarquía real a la información SMART.
  - Unificación de las etiquetas de navegación entre desktop y móvil, que divergían.
  - Corrección de los countdowns para usar la **zona horaria local del usuario** en lugar de GMT-5 hardcodeado.
  - Eliminación del componente de backlog huérfano, tras verificar que la funcionalidad real vivía embebida en la vista de Eisenhower.

**Aprendizaje de la fase:** escribir el PRD *después* de tener código funcionando resultó más útil que escribirlo antes. Obligó a justificar cada elemento existente contra la propuesta de valor, y varias features sobrevivieron el filtro solo tras ser rediseñadas.

### Fase 4 — Analítica y estado derivado *(30 de mayo)*

Objetivo: cerrar el ciclo de la metodología. Priorizar y ejecutar no sirve si el usuario no puede ver si está funcionando.

- Redacción de un **documento de diseño previo a la implementación**, evaluando tres arquitecturas posibles (todo inline / lógica separada en módulo puro / agregación en servidor) y justificando la elección de la intermedia frente a las alternativas.
- Migración del esquema para añadir `completed_at` a las tareas — requisito indispensable para cualquier métrica temporal.
- Implementación de `lib/dashboard-metrics.ts`: **cuatro funciones puras de agregación**, incluyendo la más delicada, un acumulado diario sobre una ventana móvil de 30 días que calcula una línea base con las tareas completadas *antes* de la ventana, para que la curva arranque a su altura real en lugar de desde cero.
- Manejo correcto de fechas **en hora local, no UTC**, evitando el clásico desfase de un día en los buckets diarios.
- Construcción de los cuatro componentes de gráfico sobre Recharts, cada uno con estado vacío propio y usando los tokens de color de marca para mantener coherencia en tema claro y oscuro.
- Rediseño del layout del dashboard alrededor de los gráficos como protagonistas.
- Implementación de un **sistema de estados derivados de proyecto** (`wizard` / `activo` / `vencido` / `completado` / `vencido-completado`) mediante función pura, distinguiendo explícitamente lo completado a tiempo de lo completado con retraso.

**Aprendizaje de la fase:** el gráfico de acumulado con ventana móvil parecía trivial y fue lo que más iteraciones requirió. Separar la lógica de agregación en funciones puras fue lo que permitió razonar sobre esos casos borde sin pelearse con el ciclo de renderizado de React.

---

## 6. Metodología de trabajo

Aun siendo un proyecto individual, se ejecutó con las prácticas de un equipo, deliberadamente:

- **Documentación antes de código en las fases complejas.** Cada épica no trivial arrancó con un documento de diseño que evaluaba alternativas y justificaba la elegida, seguido de un plan de implementación por pasos. Seis documentos de producto y diseño versionados junto al código.
- **Feature branches y pull requests.** Cinco PRs integrados, cada uno con su rama temática (`feat/p0-ux-headbar`, `create-user-table`, `database-connection-check`…), aunque no hubiera un revisor externo. El objetivo era mantener `main` siempre desplegable y tener un historial legible.
- **Commits convencionales y atómicos**, con prefijos semánticos (`feat`, `fix`, `chore`, `docs`) y referencia al ítem del roadmap que resuelven (`(A3)`, `(E4)`, `(C1)`) — el historial de git es trazable contra el PRD.
- **Deuda técnica registrada, no escondida.** El PRD incluye una sección propia con los seis ítems pendientes, incluyendo la ausencia de tests automatizados, declarada abiertamente como el hueco principal del proyecto y priorizada en el roadmap.
- **Despliegue continuo.** Cada merge a `main` despliega automáticamente a producción en Vercel.

---

## 7. Alcance del desarrollo: individual

**Eissential es un proyecto de desarrollo individual.** Asumí en solitario la totalidad de los roles del ciclo de vida del producto:

| Rol | Responsabilidades asumidas |
|---|---|
| **Product Manager** | Definición de la propuesta de valor y el diferenciador; definición de la persona objetivo y los jobs-to-be-done; redacción del PRD; priorización del roadmap con matriz de impacto × esfuerzo; definición de los KPIs del producto; delimitación explícita del alcance (el "no es") |
| **Diseñador de producto / UX-UI** | Sistema de diseño y tokens; jerarquía tipográfica y cromática; diseño del wizard SMART, la matriz 2×2 y el tablero Kanban; interacciones de drag & drop; comportamiento responsive y alternativas táctiles en móvil; estados vacíos y de error |
| **Arquitecto de software** | Elección del stack; estructura de carpetas y frontera dominio/persistencia; patrón de estado global con actualizaciones optimistas; separación entre derivación de datos y presentación; evaluación documentada de alternativas arquitectónicas |
| **Desarrollador frontend** | Todas las vistas y componentes; integración de Recharts; accesibilidad vía primitivos Radix; tema claro/oscuro |
| **Desarrollador backend** | Diseño del esquema Postgres; políticas RLS; sistema de autenticación completo; middleware de protección de rutas; capa de acceso a datos y conversores; endpoint de health check |
| **DevOps** | Configuración del despliegue continuo en Vercel; gestión de variables de entorno por ambiente; estrategia de ramas y PRs |

**Cómo enmarcarlo en una entrevista:** el valor de un proyecto individual de este tipo no está en la cantidad de código, sino en haber tenido que *tomar y defender* todas las decisiones —de producto, de diseño y de arquitectura— sin poder delegar ninguna. El PRD y los documentos de diseño son la evidencia de que esas decisiones se tomaron de forma explícita y razonada, no por inercia.

---

## 8. Estado actual y hoja de ruta

**Funcional y desplegado hoy:** autenticación completa, proyectos SMART con wizard y countdown, backlog, matriz de Eisenhower con drag & drop, tablero Kanban, dashboard con cuatro gráficos reales, persistencia completa en Postgres con aislamiento por usuario y health check.

**Priorizado en el roadmap:**

| Prioridad | Ítem |
|---|---|
| P1 | Animación de progreso en el wizard SMART; notificaciones de vencimiento de plazos; drag & drop robusto con `dnd-kit` y reordenamiento dentro de columna |
| P2 | OAuth (Google/GitHub); subtareas y checklists; etiquetas y filtros transversales; undo y confirmaciones en acciones destructivas; **suite de pruebas automatizadas** |
| P3 | PWA con soporte offline; perfiles de usuario; workspaces y proyectos compartidos (requiere rediseño del modelo de datos y de las políticas RLS) |

**Limitación principal reconocida:** el proyecto no tiene tests automatizados. Está documentado como deuda técnica en el PRD y priorizado como P2. La arquitectura ya se preparó para ello: la lógica de agregación y la derivación de estados están aisladas en funciones puras precisamente para ser testeables sin infraestructura de renderizado.

---

## 9. Bloques listos para usar

### 9.1 Para el CV (bullets con verbos de acción)

> **Eissential — Aplicación web de productividad** · *Proyecto individual* · Next.js 16, React 19, TypeScript, Supabase, Tailwind CSS
>
> - Diseñé y desarrollé end-to-end una aplicación de gestión de proyectos personales que unifica las metodologías SMART, matriz de Eisenhower y Kanban en un flujo guiado único, asumiendo los roles de producto, diseño, frontend, backend y despliegue.
> - Implementé un modelo de datos que **garantiza por construcción que el 100 % de las tareas cuelga de un objetivo SMART completo**, convirtiendo una buena práctica de productividad en una invariante del sistema.
> - Construí el backend sobre Supabase (Postgres + Auth): esquema relacional, políticas Row Level Security por usuario, autenticación con verificación por email y middleware de protección de rutas.
> - Desarrollé un patrón de **actualizaciones optimistas con rollback automático** en las 14 operaciones de mutación, logrando respuesta instantánea en el drag & drop sin comprometer la consistencia con el backend.
> - Diseñé un dashboard analítico con Recharts (4 visualizaciones) separando la agregación de datos en funciones puras sin React, aislando la lógica propensa a errores en unidades testeables.
> - Redacté un **PRD de 12 secciones** con auditoría de deuda técnica y roadmap de 18 ítems priorizados por impacto × esfuerzo; ejecuté el bloque P0 completo (5 ítems) en un único ciclo de entrega.

### 9.2 Para la web de portafolio (párrafo de presentación)

> **Eissential** nace de una observación simple: la mayoría de gestores de tareas te dejan anotar cualquier cosa, y por eso terminas trabajando sobre lo que grita más fuerte en lugar de sobre lo que importa. Eissential invierte el orden. No puedes crear una sola tarea hasta haber definido un objetivo SMART completo, ninguna tarea llega al tablero de ejecución sin pasar por la matriz de Eisenhower, y solo el cuadrante urgente-e-importante puede promoverse a Kanban. Es una herramienta deliberadamente opinada.
>
> La construí íntegramente en solitario —producto, diseño, frontend, backend y despliegue— sobre Next.js 16, React 19, TypeScript y Supabase. Los retos más interesantes no fueron los visibles: mantener el drag & drop instantáneo una vez añadida la persistencia real (resuelto con actualizaciones optimistas y rollback automático), garantizar el aislamiento de datos entre usuarios a nivel de base de datos, y construir la analítica temporal del dashboard con agregaciones puras y correctamente ancladas a la zona horaria local.
>
> Antes de escalar el producto escribí un PRD completo auditando lo ya construido: seis ítems de deuda técnica documentados y un roadmap de 18 ítems priorizados por impacto y esfuerzo. Ese ejercicio cambió qué se construyó después — y varias features solo sobrevivieron el filtro tras ser rediseñadas.

### 9.3 Titular corto (LinkedIn, cabecera de proyecto)

> Aplicación web de productividad que fusiona SMART, matriz de Eisenhower y Kanban en un flujo guiado y opinado. Next.js 16 · React 19 · TypeScript · Supabase · Tailwind. Desarrollo individual end-to-end: producto, diseño, arquitectura, frontend, backend y despliegue.

### 9.4 Preguntas de entrevista que este proyecto te permite responder

Guarda estas asociaciones — son las historias del proyecto mapeadas a preguntas frecuentes:

| Pregunta típica | Historia de Eissential |
|---|---|
| *Cuéntame una decisión técnica difícil* | Actualizaciones optimistas con rollback: la persistencia mató la sensación de inmediatez del drag & drop, y el drag & drop es el gesto central del producto |
| *¿Cómo priorizas?* | El PRD: 18 ítems, matriz impacto × esfuerzo, P0–P3, y la ejecución completa del P0 antes de tocar nada más |
| *¿Cómo manejas la deuda técnica?* | Sección propia en el PRD con 6 ítems; el bloque de limpieza se priorizó como P0 junto a las mejoras de UX, no después |
| *Háblame de un bug complicado* | El acumulado de la ventana móvil de 30 días: sin línea base, la curva arrancaba en cero y mentía; y el desfase de un día por usar UTC en lugar de hora local |
| *¿Cómo diseñas para mantenibilidad?* | Estado derivado en lugar de almacenado, y la frontera dominio↔base de datos con conversores centralizados |
| *¿Qué harías distinto?* | Escribir tests desde el principio — está documentado como el hueco principal y la arquitectura ya está preparada para cerrarlo |

---

*Documento generado a partir del análisis del código, la documentación de producto y el historial de desarrollo del repositorio.*
