# FoodLinks — Documento base para CV y portafolio

> **Qué es este archivo:** material de referencia sobre el proyecto FoodLinks y sobre mi participación concreta en él. Está pensado para alimentar la redacción de mi CV, mi portafolio web y mis respuestas en entrevistas. Todo lo que aparece aquí es verificable en el historial de commits de los dos repositorios del proyecto.

---

## 1. Resumen ejecutivo

**FoodLinks** es una plataforma móvil que conecta a **comerciantes de mercado** que terminan el día con excedentes de alimentos en buen estado con **comedores comunitarios** que los necesitan, y que registra el impacto ambiental de cada rescate.

El problema que ataca no es de escasez, es de **coordinación**. El comerciante tiene la comida y el comedor la necesita, pero entre ambos no existe un canal: la información sobre qué hay disponible, dónde, cuánto y hasta qué hora sirve viaja hoy por llamadas sueltas, grupos de WhatsApp o simplemente no viaja. El resultado es que el alimento se pierde no por falta de demanda, sino por falta de un sistema que empareje oferta y demanda **antes de que el reloj se acabe**.

FoodLinks convierte ese emparejamiento en un flujo digital de cuatro pasos —publicar, reservar, verificar el recojo y medir el impacto— con **tiempo límite explícito** en cada donación y **liberación automática** del lote cuando ese tiempo vence, para que ninguna reserva abandonada bloquee comida que otro comedor sí habría recogido.

- **Tipo de proyecto:** académico universitario (Universidad Nacional Mayor de San Marcos).
- **Modalidad:** desarrollo **grupal**, equipo de 5 personas.
- **Periodo:** mayo – julio de 2026 (~10 semanas de desarrollo activo).
- **Mi rol:** Desarrollador Frontend Mobile y responsable del sistema de diseño y de la definición de requerimientos funcionales hacia el backend.
- **Repositorios:** dos, separados por capa — backend (API REST) y frontend (app móvil).

---

## 2. El problema, en detalle

Un puesto de mercado que vende productos perecibles cierra con excedente casi todos los días: fruta madura, verdura fuera de calibre, pan del día. Ese excedente tiene una ventana de utilidad muy corta —horas, no días— y tres finales posibles: se remata, se regala a quien pase, o se bota.

Del otro lado, un comedor comunitario opera con presupuesto fijo y menú planificado. Sabe que ese excedente existe, pero no sabe **cuál**, **cuánto**, **dónde** ni **hasta cuándo**, y no puede permitirse mandar a alguien a recorrer el mercado a preguntar.

Las tres fricciones concretas que el sistema tenía que resolver:

1. **Falta de visibilidad.** No hay un lugar donde ver, en un solo listado, lo que está disponible ahora mismo cerca del comedor.
2. **Falta de compromiso verificable.** Cuando la coordinación es informal, el comerciante no sabe si el comedor va a ir realmente, y el comedor no sabe si al llegar el lote todavía estará ahí. Ambos asumen un costo si el otro falla.
3. **Falta de trazabilidad.** Nadie registra cuánto se rescató. Sin ese dato, ni el comedor puede mostrar resultados a quien lo financia, ni el comerciante puede acreditar su aporte, ni el proyecto puede demostrar que funciona.

---

## 3. La solución: cómo funciona el producto

La app tiene **dos roles** que comparten la misma aplicación pero ven flujos distintos:

| Rol | Quién es | Qué hace en la app |
|---|---|---|
| `Comerciante` | Vendedor de mercado con excedentes | Publica lotes (descripción, kilos, foto, tiempo límite, caducidad), ve su historial y su impacto acumulado |
| `GestorComedor` | Encargado de un comedor comunitario | Explora el feed de donaciones disponibles, reserva, coordina el recojo y registra la frescura recibida |

### El flujo completo

1. **Publicación.** El comerciante registra un lote con cantidad en kilos, foto, horario de atención de su puesto y un `tiempo_limite` de recojo. El lote entra al feed como `Disponible`.
2. **Descubrimiento.** El gestor del comedor ve el feed con las donaciones abiertas, cada una con su contador de tiempo restante y el horario en que puede pasar a recogerla. También puede verlas geolocalizadas en un mapa junto con el resto de puestos y comedores de la red.
3. **Reserva.** Al reservar, el lote pasa a `Reservado` y el sistema genera un **código de verificación único** que el comedor recibe como **código QR y como PIN numérico**. El doble formato es deliberado: el QR es rápido, pero el PIN funciona cuando la cámara falla, cuando hay poca luz en el puesto o cuando el celular del comerciante es de gama baja.
4. **Recojo verificado.** En el punto de encuentro, el comerciante valida el código. La reserva pasa a `Validado` y luego a `Entregado`, `Rechazado` o `Cancelado` según lo que ocurra realmente. La calificación de frescura (1–5) solo se habilita cuando el recojo está validado, para que ninguna valoración exista sin una entrega real detrás.
5. **Impacto.** Cada recojo confirmado registra los kilos rescatados, la fecha, el puntaje de frescura y el **CO₂ equivalente evitado**, calculado sobre el peso del lote. La pantalla de impacto muestra el acumulado y el historial.
6. **Expiración automática.** Un proceso en segundo plano recorre periódicamente las reservas cuyo tiempo límite venció y las cancela, devolviendo el lote al estado `Disponible`. Esto es lo que impide que una reserva olvidada mate una donación que aún era útil.

### La decisión de producto más importante

**El tiempo es el recurso escaso, no la comida.** Todo el sistema está construido alrededor de esa idea: el tiempo límite es obligatorio al publicar, el contador es un elemento visual de primer nivel en cada tarjeta, el color naranja de la marca está reservado exclusivamente para señalar urgencia, y la expiración es automática en vez de manual. Un diseño que tratara las donaciones como un catálogo de e-commerce habría fallado exactamente en el punto donde el problema real ocurre.

---

## 4. Arquitectura y stack técnico

El proyecto está dividido en dos repositorios independientes que se comunican por HTTP.

### Backend — API REST

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migraciones | Alembic |
| Base de datos | PostgreSQL (Supabase) |
| Almacenamiento de imágenes | Supabase Storage |
| Autenticación | JWT + bcrypt, con Google Sign-In integrado |
| Tareas programadas | APScheduler / loop `asyncio` en el `lifespan` de la app |
| Pruebas | pytest + `TestClient`, con SQLite en memoria por test |
| CI | GitHub Actions (pruebas y cobertura en cada push y PR a `main`/`develop`) |
| Pruebas de carga | Locust y un script de estrés interno con `ThreadPoolExecutor` |

Organización por capas: `routers/` (endpoints) → `services/` (reglas de negocio) → `models/` (ORM) → `schemas/` (contratos Pydantic), con `core/` para configuración por entorno y `db/` para sesiones. Esta separación permitió que las reglas de negocio —transiciones de estado de una reserva, cálculo de CO₂, expiración— fueran testeables sin levantar HTTP.

**Modelo de datos:** `usuarios`, `puestos_mercado`, `comedores`, `donaciones_lotes`, `reservas` y `trazabilidad_valoracion`.

### Frontend — Aplicación móvil

| Componente | Tecnología |
|---|---|
| Framework | React Native 0.85 sobre Expo SDK 56 |
| Lenguaje | TypeScript |
| Navegación | Expo Router (file-based routing) |
| Cliente HTTP | Axios, con capa `src/api/` tipada |
| Mapas | `expo-maps` (migrado desde `react-native-maps`) |
| Cámara e imágenes | `expo-camera`, `expo-image-picker`, `expo-image` |
| QR | `react-native-qrcode-svg` |
| Autenticación social | `@react-native-google-signin/google-signin` |
| Compilación y distribución | EAS Build + `expo-updates` |

Estructura por rol y por responsabilidad: `src/app/comedor/` y `src/app/comerciante/` para las pantallas de cada perfil, `src/api/` como única frontera con el backend (cliente, tipos, errores y un módulo por dominio), `src/components/` para piezas compartidas con variantes `.web.tsx` donde la plataforma lo exige, `src/utils/` para lógica pura y `src/context/` para la sesión.

---

## 5. Métricas

Distingo tres bloques, porque en una entrevista no vale lo mismo un número medido que un número modelado.

### 5.1 Métricas de impacto que el sistema está diseñado para optimizar *(proyectadas)*

> **Nota de honestidad:** el proyecto llegó a MVP funcional en contexto académico, no a operación con usuarios reales sostenidos. Las cifras siguientes son **proyecciones modeladas** sobre un escenario piloto, con los supuestos declarados de forma explícita. Sirven para explicar **qué optimiza el producto y cómo se mediría**, no para afirmar resultados obtenidos.

**Supuestos del escenario piloto:** 1 mercado con 30 puestos adheridos y 10 comedores en un radio de 2 km; excedente aprovechable promedio de 3 kg por puesto por día de operación; 26 días de operación al mes; tasa de emparejamiento efectivo del 60 % (proporción de lo publicado que efectivamente se reserva y recoge dentro del tiempo límite); factor de 2,5 kg de CO₂e evitados por kg de alimento rescatado —el mismo factor que implementa el backend en el cálculo de trazabilidad—; y 0,4 kg de alimento por ración servida.

| Métrica | Modelo | Resultado proyectado (mensual) |
|---|---|---|
| Alimento publicado | 30 puestos × 3 kg × 26 días | **2 340 kg** |
| Alimento efectivamente rescatado | 2 340 kg × 60 % | **~1 400 kg** |
| CO₂ equivalente evitado | 1 400 kg × 2,5 | **~3 500 kg CO₂e** |
| Raciones habilitadas | 1 400 kg ÷ 0,4 | **~3 500 raciones** |
| Comedores beneficiados | — | **10** |

**Métricas que el producto permite medir y sobre las cuales se optimiza:**

- **Tasa de rescate** — kg recogidos ÷ kg publicados. Es la métrica norte del producto. Todo el diseño del tiempo límite, del contador visual y de la expiración automática existe para subirla.
- **Tasa de expiración** — lotes que vencen sin ser reservados, o reservas que vencen sin recojo. Es la métrica de pérdida y el sistema la registra de forma automática al expirar.
- **Tiempo de publicación a reserva** — cuánto tarda un lote en encontrar comedor. Mide qué tan líquida es la red.
- **Tasa de recojos verificados** — recojos validados con QR/PIN sobre el total de reservas. Mide el compromiso real y es la métrica que justifica todo el mecanismo de verificación.
- **Puntaje de frescura promedio** (1–5) — mide la calidad de lo donado y permite detectar puestos que usan la plataforma para deshacerse de producto no apto.
- **CO₂ acumulado por comedor** — el dato que un comedor puede llevar a un donante o a un municipio para sustentar su gestión.

**Fricción operativa que el sistema reduce:** la coordinación informal de una donación por llamadas y mensajes implica varios intercambios entre ambas partes y no deja registro. En FoodLinks la publicación es un formulario y la reserva es un toque, con confirmación inmediata y trazabilidad automática. La ganancia no está solo en minutos ahorrados, sino en que **el registro del rescate deja de depender de que alguien se acuerde de anotarlo**.

### 5.2 Métricas de producto e ingeniería *(reales, verificables en el repositorio)*

- **129 commits** entre ambos repositorios (71 en backend, 58 en frontend) en ~10 semanas.
- **13 pantallas** en la app móvil, repartidas en dos flujos de rol independientes más autenticación y perfil.
- **12+ endpoints REST** cubriendo autenticación, donaciones, reservas, trazabilidad, impacto y utilidades de desarrollo.
- **6 entidades** de dominio con migraciones versionadas en Alembic.
- **5 estados** de reserva con transiciones validadas tanto en el modelo ORM como en el `CHECK constraint` de la base de datos.
- **Integración continua** en GitHub Actions ejecutando la suite de pruebas y reporte de cobertura en cada push y PR a `main` y `develop`.
- **Umbral de rendimiento definido en la prueba de carga:** el escenario de Locust marca como fallida toda respuesta del feed de donaciones que supere **500 ms**, simulando usuarios concurrentes con tiempos de espera de 0,5 a 1,5 s entre peticiones.
- **Sistema de diseño documentado:** ~1 180 líneas entre la especificación de tokens (`docs/design.md`) y la guía visual navegable (`docs/design.html`).

### 5.3 Métricas de accesibilidad y calidad de interfaz *(reales, por diseño)*

- **Contraste 9,3:1** en el par de color primario, muy por encima del mínimo AA de 4,5:1.
- **Objetivos táctiles de 52 px** de alto en los botones principales, frente al mínimo recomendado de 44 px — decisión tomada porque la app se usa de pie, con prisa y a veces con las manos ocupadas.
- **Cero dependencia del color como único portador de información:** cada estado del dominio se comunica con color *y* etiqueta de texto, lo que mantiene la app usable para personas con daltonismo.
- **Doble vía de verificación** (QR + PIN) como redundancia deliberada ante fallos de cámara, iluminación o hardware de gama baja.

---

## 6. Mi contribución al proyecto

Trabajé principalmente en la **capa frontend** y asumí dos responsabilidades transversales: el **sistema de diseño** y la **especificación de requerimientos hacia el backend** cuando una necesidad de la app no estaba cubierta por la API.

### 6.1 Flujo de verificación de recojo (QR + PIN)

Diseñé e implementé la pantalla de verificación que cierra el ciclo de reserva. Al reservar, el gestor del comedor recibe un código único renderizado simultáneamente como **QR escaneable** y como **PIN legible en pantalla**, pensado para mostrarse a un metro de distancia o dictarse en voz alta.

Antes de escribir código, redacté el requerimiento correspondiente para el backend —generación y exposición del código de verificación en el recurso de reserva— porque la funcionalidad no existía del lado del servidor. La pantalla también contempla el caso de fallo: si el código no se pudo generar, muestra un estado de error explícito con una salida clara en vez de una pantalla en blanco.

**Aporte:** eliminó la ambigüedad del momento del encuentro. Antes, "recoger la donación" era un acuerdo verbal sin evidencia; después, es una transacción con confirmación de ambas partes y registro persistente.

### 6.2 Flujo de recojos y máquina de estados de la reserva

Implementé la pantalla de recojos del comedor con manejo completo de estados y las confirmaciones destructivas asociadas: rechazar una entrega y cancelar una reserva. Extraje esa lógica de confirmación a una utilidad reutilizable (`src/utils/confirmar.ts`) para que el patrón fuera consistente en toda la app en vez de repetirse pantalla por pantalla.

Este trabajo destapó un **bug de integridad en la base de datos** que documenté y especifiqué para el backend: el modelo ORM declaraba los cinco estados de reserva, pero el `CHECK constraint` creado en la migración inicial solo permitía tres. Ninguna migración posterior lo había corregido, así que la base de datos en producción rechazaba los estados `Validado` y `Rechazado` — lo que rompía silenciosamente el propio endpoint de confirmación de recojo. Escribí el requerimiento con la migración de Alembic necesaria, los cambios en el esquema Pydantic para exponer el estado, el ajuste del filtro que omitía las reservas ya validadas, y la decisión de producto de permitir cancelar antes de validar.

Del lado del backend, implementé la transición de estado a `Validado` en el servicio de reservas.

**Aporte:** este es el trabajo del que más orgulloso estoy, porque no fue escribir una pantalla: fue **detectar una inconsistencia entre el modelo, la migración y el comportamiento real de la base de datos**, entender su alcance completo y entregar la especificación con la solución en vez de un reporte de "no funciona". Mientras el backend integraba el cambio, dejé el frontend avanzando con un flag de mock explícito y documentado, para no bloquear el resto del desarrollo.

### 6.3 Geolocalización: mapa de puestos y comedores

Implementé la funcionalidad de mapa para ambos roles: un servicio de ubicaciones en la capa de API, los tipos correspondientes, el componente de mapa con marcadores diferenciados para puestos de mercado y comedores, la variante web del componente y la integración como pestaña en la navegación de los dos perfiles.

Redacté además el requerimiento de backend para que las entidades expusieran coordenadas GPS, ya que el modelo de datos original no las contemplaba.

**Aporte:** convirtió una decisión abstracta ("¿reservo esta donación?") en una decisión informada por distancia. Para un comedor con recursos limitados de transporte, la ubicación no es un adorno: es el factor que determina si el rescate es viable.

### 6.4 Visibilidad temporal: horarios de atención y tiempo restante

Implementé la lógica de horarios (`src/utils/horarios.ts`) y su integración en el feed del comedor y en el formulario de publicación del comerciante: formato de hora en 12 h legible, rango de atención del puesto y cálculo de tiempo restante expresado en la unidad más relevante ("2 días", "3 horas", "45 minutos", con singular y plural correctos).

También agregué la notificación de cancelación automática por vencimiento en el historial del comerciante, para que la expiración de un lote no fuera un evento invisible.

**Aporte:** cerró la brecha entre el dato crudo y la decisión. Una fecha ISO en pantalla no le dice nada a alguien apurado; "quedan 45 minutos" sí. Es la traducción de un timestamp a una decisión.

### 6.5 Sistema de diseño

Definí y documenté el sistema de diseño completo de FoodLinks en dos artefactos espejo: una **especificación de tokens** en YAML con su racional escrito (`docs/design.md`) y una **guía visual navegable** que renderiza cada token y componente en vivo (`docs/design.html`).

Incluye paleta completa con pares de contraste verificados, escala tipográfica de tres zonas con un nivel numérico dedicado —para que los kilos y los contadores no "bailen" al actualizarse—, escala de espaciado de 4 px, sistema de formas con una regla legible de un vistazo (*si es pill, es tocable; si tiene esquina de 16 px, es contenido*), y el catálogo de componentes del dominio: tarjeta de lote, badges por estado, contador de urgencia en tres niveles, bloque de código de verificación y estados vacíos.

Dos decisiones que defiendo especialmente:

- **El naranja tiene un solo trabajo: urgencia temporal.** No es un segundo color de marca de uso libre. Si el naranja aparece en todas partes, deja de significar "esto vence pronto" y el sistema pierde su señal más importante.
- **Jerarquía por contraste de superficie, no por sombras.** Además de dar la sensación de calma que el producto necesitaba, elimina una fuente clásica de deriva visual entre iOS y Android, donde las sombras de React Native se comportan de forma distinta.

**Aporte:** dio al equipo un vocabulario compartido y decisiones tomadas de antemano, en vez de que cada pantalla reinventara sus propios colores y espaciados.

### 6.6 Puentes con el backend y calidad del entorno

Redacté cinco documentos de requerimiento funcional para el backend, cada uno partiendo de una necesidad concreta del frontend y llegando hasta el cambio propuesto a nivel de esquema, servicio y migración. Además fijé la versión de Node del proyecto (`.nvmrc`), migré la configuración de la app a `import type` y establecí en el archivo de convenciones del equipo las reglas de mensajes de commit.

### Resumen de mi participación

**11 commits en el repositorio frontend y 5 en el backend**, concentrados en: pantalla de verificación QR/PIN, flujo completo de recojos con máquina de estados, mapa de ubicaciones para ambos roles, lógica de horarios y tiempo restante, notificación de expiración automática, sistema de diseño completo y cinco especificaciones de requerimiento hacia el backend.

---

## 7. Modalidad de desarrollo: proyecto grupal

**FoodLinks fue un desarrollo grupal de 5 personas**, en el marco de un proyecto universitario de la UNMSM, entre mayo y julio de 2026.

### Cómo se organizó el equipo

- **Dos repositorios separados** por capa, con el contrato de la API como frontera entre ambos.
- **Reparto por especialidad y por tarea:** el trabajo se dividió en tareas numeradas asignadas por integrante, cada una desarrollada en su propia rama.
- **Flujo de trabajo con Git:** ramas por tarea o por feature (`Tarea3`, `feature/vista-qr-pin`, `CambiarSDK56`, `Conexion_GCP`), integración vía **Pull Requests** hacia `main` y `develop`. Se registraron 12 PRs en el backend y 11 en el frontend.
- **Convenciones de commit acordadas y documentadas** en un archivo de convenciones del equipo: mensajes en español, formato convencional (`feat(scope): ...`, `fix(scope): ...`).
- **CI compartido:** GitHub Actions ejecutando la suite de pruebas y la cobertura en cada push y PR, de modo que un cambio de un integrante no rompía silenciosamente el trabajo de otro.
- **Comunicación entre capas mediante documentos de requerimiento escritos**, versionados en el propio repositorio del backend. Cuando el frontend necesitaba algo que la API no exponía, no se resolvía por chat: se escribía la especificación con contexto, cambio propuesto y criterio de integración.

### Qué significó eso para mi trabajo

Trabajar en un equipo repartido entre dos repositorios significó que **la mitad de mi trabajo fue de interfaz humana, no solo de código**: identificar que algo faltaba del lado del servidor, entender la lógica del backend lo suficiente para proponer el cambio concreto —incluida la migración de base de datos—, y dejar el frontend avanzando con mocks explícitos y documentados mientras la integración llegaba. Ninguna de mis tareas se quedó bloqueada esperando a otra capa.

---

## 8. Retos técnicos y decisiones de diseño

**Inconsistencia entre modelo, migración y base de datos real.** El caso ya descrito del `CHECK constraint` de estados de reserva. La lección: un modelo ORM correcto no garantiza una base de datos correcta si las migraciones no lo siguieron. Y el síntoma no fue un error de tipos en desarrollo, sino un endpoint que fallaba solo contra la base de datos real.

**Trabajar contra una API en construcción.** Varias pantallas necesitaban datos que el backend aún no exponía. La estrategia fue introducir flags de mock explícitos y nombrados (`USAR_MOCK_ESTADO`), con la instrucción de integración escrita junto al requerimiento, en vez de valores hardcodeados que después nadie recuerda dónde están.

**Paridad entre plataformas.** Los mapas y algunos componentes se comportan distinto en móvil y en web. Se resolvió con variantes `.web.tsx` por componente en vez de condicionales de plataforma dispersos por el código. En el sistema de diseño, la decisión de evitar sombras respondió al mismo problema: las sombras de React Native divergen entre iOS y Android.

**Diseñar para el contexto de uso real, no para la captura de pantalla.** La app se usa de pie, en un mercado, con prisa y con poca luz. De ahí salen los botones de 52 px, el código en tipografía display legible a un metro, el PIN como respaldo del QR y el espaciado generoso que sacrifica densidad a cambio de que ninguna tarjeta de lote se lea mal.

---

## 9. Aprendizajes

- **Escribir el requerimiento es parte del trabajo del frontend.** Detectar que falta algo del otro lado no es un bloqueo, es una entrega: contexto, cambio propuesto y criterio de aceptación.
- **Un sistema de diseño no es una paleta de colores; es un conjunto de decisiones ya tomadas.** Su valor real aparece cuando otro integrante del equipo construye una pantalla que no habías previsto y aun así encaja.
- **Las restricciones del contexto de uso mandan sobre la estética.** El mejor argumento de diseño de este proyecto —reservar el naranja exclusivamente para la urgencia— salió de entender el dominio, no de una referencia visual.
- **La trazabilidad automática vence a la disciplina humana.** El CO₂ se registra solo, al confirmar el recojo. Si dependiera de que alguien lo anote, el dato no existiría.

---

## 10. Material listo para usar

### Viñetas para CV

> **FoodLinks — App móvil de redistribución de alimentos** · *Desarrollador Frontend Mobile · Proyecto universitario grupal (5 personas) · May–Jul 2026*
>
> - Desarrollé la app móvil en **React Native / Expo SDK 56 + TypeScript** para una plataforma que conecta comerciantes de mercado con comedores comunitarios, implementando 13 pantallas repartidas en dos flujos de rol independientes.
> - Diseñé e implementé el **flujo de verificación de recojo con QR y PIN** de doble vía, junto con la máquina de estados de reserva de 5 estados que garantiza que ninguna valoración exista sin una entrega confirmada.
> - **Detecté y especifiqué la corrección de un bug de integridad de datos crítico**: un `CHECK constraint` de PostgreSQL desalineado con el modelo ORM que rompía silenciosamente el endpoint de confirmación de recojo en producción; entregué el requerimiento con la migración de Alembic y los cambios de esquema necesarios.
> - Definí el **sistema de diseño completo** (~1 180 líneas de tokens documentados y guía visual navegable), con contraste verificado hasta 9,3:1, objetivos táctiles de 52 px y estados que nunca dependen solo del color.
> - Implementé **geolocalización con mapas** para ambos roles y la lógica de urgencia temporal (horarios de atención, tiempo restante legible y notificación de expiración automática), que son el núcleo de la métrica de rescate del producto.
> - Trabajé con **Git flow por ramas y Pull Requests** sobre dos repositorios con CI en GitHub Actions, redactando 5 especificaciones de requerimiento funcional hacia el equipo de backend.

### Párrafo corto para portafolio (~60 palabras)

> **FoodLinks** conecta a comerciantes de mercado con excedentes de alimentos con comedores comunitarios que los necesitan, y mide el CO₂ evitado en cada rescate. Desarrollé la app móvil en React Native y Expo: el flujo de verificación de recojo con QR y PIN, la máquina de estados de reserva, los mapas de ubicaciones y el sistema de diseño completo. Proyecto universitario grupal de 5 personas.

### Párrafo medio para portafolio (~140 palabras)

> El alimento no se pierde por falta de demanda, sino por falta de coordinación: un comerciante de mercado cierra con excedente aprovechable y un comedor comunitario a dos cuadras lo necesita, pero entre ambos no hay canal ni reloj compartido.
>
> **FoodLinks** es la app móvil que crea ese canal. El comerciante publica su lote con tiempo límite, el comedor lo reserva y recibe un código QR con respaldo en PIN, el recojo se verifica en el punto de encuentro y el sistema registra automáticamente los kilos rescatados y el CO₂ equivalente evitado. Si una reserva vence, el lote se libera solo.
>
> Trabajé como desarrollador frontend en un equipo de 5 personas: construí el flujo de verificación y recojos, la geolocalización, la lógica de urgencia temporal y el sistema de diseño completo. Stack: React Native, Expo SDK 56, TypeScript; backend en FastAPI y PostgreSQL.

### Frase de una línea

> App móvil que rescata excedentes de mercados para comedores comunitarios, con verificación de recojo por QR/PIN y medición automática de CO₂ evitado.
