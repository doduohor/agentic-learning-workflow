# Инструкция агенту: C4-диаграммы через Structurizr DSL

Рабочая инструкция для создания и изменения C4-моделей в Structurizr DSL. Пиши
объяснения по-русски, а официальные названия, DSL-ключевые слова, identifiers,
tags и команды оставляй в оригинальном виде.

Локальная основа правил — [исследовательская заметка](../diagrams/structurizr-dsl-for-agents-research.md).
Для спорных, version-sensitive и зависящих от версии CLI деталей открой
официальные ссылки из этой заметки.

## Когда использовать инструкцию

Прочитай этот документ, если задача просит создать или изменить C4-диаграмму
через Structurizr DSL: System Landscape, System Context, Container, Component,
Dynamic, Deployment, Filtered, Custom или Image view. Он подходит для моделей
разных систем и не заменяет документацию Structurizr.

Не используй его как руководство для UML, BPMN, ERD, sequence diagram без C4
модели или произвольного рисунка. Custom и Image views применяй только когда
обычная C4 view не выражает нужную информацию и это решение явно объяснено.

## Обязательный порядок работы

1. Уточни цель, аудиторию, границу системы и требуемый уровень C4. Если цель
   неясна, зафиксируй разумное допущение в ответе.
2. Осмотри существующий DSL, связанные документы и правила репозитория. При
   изменении сохраняй существующие identifiers, tags и публичные views без
   необходимости их переименовывать.
3. Составь список элементов, отношений и нужных views. Правило: сначала модель, потом views.
   Объявления элементов и static relationships должны существовать до
   ссылок на них в представлениях.
4. Создай или измени workspace минимальным DSL-шаблоном ниже. Каждое новое
   отношение подпиши действием и протоколом/технологией, если это помогает
   понять архитектуру.
5. Добавь только views, отвечающие цели. Для Dynamic сначала проверь static
   relationship; для Deployment отдели логическую модель от runtime topology.
6. Настрой tags, styles, themes, terminology и документационные ссылки только
   после того, как модель и views понятны.
7. Выполни проверки из раздела «Проверка результата», затем сообщи отдельные
   результаты проверки DSL, экспорта и архитектурного анализа.

Критерий завершения: цель пользователя покрыта выбранными views, каждый
показанный элемент и arrow объяснимы, DSL проверен доступным способом, а
ограничения проверки явно указаны.

## Минимальный шаблон DSL

Начинай с каркаса и расширяй его по необходимости:

```dsl
workspace "Название" "Короткое назначение" {
    model {
        user = person "Пользователь" "Кто взаимодействует с системой"
        system = softwareSystem "Система" "Главная граница модели" {
            api = container "API" "Принимает запросы" "Kotlin/Ktor"
            db = container "База данных" "Хранит данные" "PostgreSQL" {
                tags "Database"
            }
            api -> db "Читает и записывает данные" "SQL"
        }
        user -> system "Использует" "HTTPS"
    }

    views {
        systemContext system "SystemContext" {
            include *
            autoLayout lr
        }
        styles {
            element "Person" { shape Person }
            element "Database" { shape Cylinder }
        }
    }
}
```

`workspace` оборачивает `model` и `views`; `model` содержит элементы и
отношения, а `views` — представления и оформление. Для реального workspace
добавляй descriptions, titles и уникальные view keys, но не превращай шаблон в
пример конкретного домена.

## Правила моделирования C4

- `person` — пользователь, роль или внешний актор; `softwareSystem` — система,
  которую рассматривают как единицу; `container` — приложение, сервис,
  хранилище или другой исполняемый/развёртываемый блок внутри системы;
  `component` — часть контейнера с более детальной ответственностью.
- System Landscape показывает несколько систем и людей без обязательной
  фокусировки на одной системе. System Context показывает выбранную систему и
  её внешних участников. Container раскрывает внутренние containers, Component
  — компоненты конкретного container.
- Dynamic показывает порядок сообщений для одного сценария, а не полный
  статический состав системы. Deployment показывает, где logical elements
  работают в runtime; он не заменяет Container или Component view.
- Каждое отношение должно отвечать на вопрос «кто с кем и зачем/как
  взаимодействует». Не добавляй стрелки только ради плотности графа.
- Implied relationships включай, только если автоматически выведенные связи
  помогают читателю и не скрывают важную границу. Иначе явно настрой
  `!impliedRelationships false` и опиши нужные связи вручную.

## Идентификаторы и порядок объявления

Присваивай стабильный identifier каждому элементу, на который ссылаются
relationships, views, deployment instances, `include`/`exclude` или Dynamic.
Для сложного workspace используй иерархию, например `bookingSystem.api` и
`bookingSystem.api.bookingController`; она уменьшает коллизии и делает ссылки
читаемыми. Relationship identifiers задавай осознанно, если на них будут ссылки.

Объявляй элемент до любого отношения или view, которое его использует:
forward reference безопасно не предполагай. В scoped-блоке системы или
контейнера `this` означает текущий scope; применяй его для локальных отношений,
но проверяй, что левая и правая стороны действительно имеют нужный scope.
Group names, element identifiers и relationship identifiers не смешивай.
При изменении существующего файла сначала найди все ссылки на переименуемый
identifier и обнови их атомарно.

## Relationships

Пиши отношение как `source -> destination "Описание" "Технология"` и выбирай
направление по фактическому потоку зависимости/запроса. Описание должно быть
глаголом или коротким действием: `Получает заявку`, `Публикует событие`,
`Читает данные`. Технологию указывай только если она известна и полезна.

Сначала создай static relationship в `model`, затем используй его в views и
Dynamic. Не моделируй в Dynamic связь, которой нет в статической модели. Для
повторяющихся отношений используй явные identifiers и проверяй, что не создал
дубликат с другой подписью. Implied relationships рассматривай как удобство
визуализации, а не замену значимым явным контрактам.

## Выбор view

| Цель | View | Граница |
| --- | --- | --- |
| Все люди и системы | `systemLandscape` | широкий ландшафт |
| Одна система и окружение | `systemContext` | выбранная `softwareSystem` |
| Внутренние части системы | `container` | containers системы |
| Детали одного контейнера | `component` | components container |
| Один сценарий поведения | `dynamic` | выбранная область и порядок шагов |
| Runtime и инфраструктура | `deployment` | environment и deployment nodes |
| Подмножество базовой view | `filtered` | tags/relationships поверх base view |
| Нестандартная композиция | `custom` | только при оправданной необходимости |
| Внешнее изображение | `image` | только когда C4-элемент должен ссылаться на bitmap |

У каждой view должен быть уникальный key и понятный title/description. Не
пытайся одной view одновременно объяснить контекст, внутреннюю структуру и
runtime-сценарий.

Для Deployment view в `model` объяви `deploymentEnvironment` для каждого
значимого окружения (`Development`, `Staging`, `Production`). Внутри environment
строй вложенные `deploymentNode` (кластер, host, container platform), при
необходимости добавляй `infrastructureNode` (load balancer, firewall, DNS), а
логические системы и containers размещай как `softwareSystemInstance` и
`containerInstance`; `instanceOf` используй только как понятное сокращение.
`deploymentGroup` помогает показать группу связанных экземпляров и не является
новым логическим container. Связи deployment-уровня задавай отдельно и не
подменяй ими отношения логической модели. Не смешивай environment, node и
instance с элементами Container/Component view.

## Правила `include *`

`include *` означает «включить доступные элементы в текущей области view», а
не «показать буквально всю модель». Его смысл зависит от типа view:
Иными словами, `include *` зависит от типа view и текущей области.

| View | Что обычно включает `include *` |
| --- | --- |
| `systemLandscape` | людей и software systems workspace |
| `systemContext` | выбранную систему и внешние элементы, связанные с ней |
| `container` | containers выбранной системы и связанные элементы |
| `component` | components выбранного container и связанные элементы |
| `dynamic` | `include *` не применяется; static scope и шаги задаются явно |
| `deployment` | deployment elements текущего environment/scope |

Считай таблицу правилом выбора области, а не обещанием конкретного состава:
проверь фактический результат и при необходимости используй `include`,
`exclude`, `*?` (тот же набор scoped-элементов, но только отношения к/от
scoped-элемента) и
relationship expressions. Явные include/exclude предпочтительнее, когда view
должна быть стабильным архитектурным срезом. В Filtered view сначала укажи
`base` view и tags/режим фильтра. Учти, что после создания Filtered view
исходная base view обычно исчезает из списка renderer; если нужны обе, добавь
в filtered view `include "Element,Relationship"`.

## Dynamic view

Выбирай один сценарий с началом и завершением: например бронирование места,
публикация события или обработка ошибки. Каждый шаг имеет монотонный номер и
краткое описание; номера должны отражать порядок, а не внутренние database IDs.
Каждый `source -> destination` в Dynamic должен соответствовать существующему
static relationship с той же парой элементов (и, если задано, корректным
relationship identifier). Если сообщения идут в обе стороны, создай обе
статические связи.

Ограничь Dynamic view участниками и шагами, нужными для сценария. Параллельные
или альтернативные ветви опиши в тексте/отдельной view, если порядок нельзя
однозначно прочитать по номерам. Dynamic view объясняет поведение и не должна
становиться заменой Container/Component view.

## Стили и терминология

Рассматривай tags как API оформления: сначала назначь смысловые tags, затем
определи общие `styles` для элементов и relationships. Не кодируй смысл только
цветом; сохраняй читаемые названия и descriptions. Shared styles должны быть
минимальными и переиспользуемыми, а workspace overrides — намеренными и
документированными.

Themes подключай через theme tags и проверяй, какие локальные overrides
перекрывают тему. `terminology` можно использовать для адаптации подписей под
домен, но не меняй этим семантику C4-уровней. Перед экспортом учитывай, что
Mermaid, PlantUML и другие форматы могут не поддерживать все shapes, routing,
цвета, themes или properties; проверяй именно запрошенный формат.

## Модульность

`!include` используй для небольших связанных DSL-файлов с безопасными
относительными путями внутри разрешённого workspace. Проверь порядок загрузки:
подключённый файл должен объявлять сущности до их использования. Workspace
extension применяй, когда нужно расширить согласованную базовую модель, и
проверь, какие model/views/styles переопределяются.

`!docs` и `!adrs` связывают элементы с Markdown/AsciiDoc-документами и ADR.
Храни пути рядом с workspace, не используй непроверенные абсолютные пути и не
подключай файлы за пределами ожидаемого дерева. Документация объясняет решение,
но не должна быть способом спрятать отсутствующую модель или отношение.

## Проверка результата

1. Если доступен Structurizr CLI, запусти его валидацию для изменённого DSL и
   исправь все синтаксические/модельные ошибки до заявления о валидности.
2. Если пользователь запросил SVG, PNG, HTML, Mermaid, PlantUML или другой
   экспорт, создай только запрошенный артефакт и проверь его содержимое,
   читаемость, наличие ожидаемых элементов и потери стилей.
3. Если Structurizr CLI недоступен, выполни fallback: проверь парность скобок,
   наличие `workspace`/`model`/`views`, уникальность ключевых identifiers,
   порядок объявлений, ссылки include/exclude и сопоставь каждый Dynamic шаг со
   static relationship. Честно сообщи, что CLI validation не запускалась.
4. Отдельно проведи архитектурный review: правильный ли C4-уровень выбран,
   не потеряны ли внешние зависимости, нет ли misleading стрелок, достаточно ли
   описаний и не смешаны ли logical model с deployment topology.

Проверка синтаксической валидности DSL — необходимое, но недостаточное условие качества.
Успешный parser не доказывает полноту модели, правильность границ системы или
полезность архитектурного объяснения.

## Чеклист типичных ошибок

- [ ] Цель и аудитория view записаны; выбран ровно подходящий C4-уровень.
- [ ] Сначала описана модель, затем views; нет небезопасных forward references.
- [ ] Ссылочные элементы имеют стабильные identifiers; переименование проверено поиском.
- [ ] Relationships направлены, содержательны и не дублируют без причины implied relationships.
- [ ] `include *` интерпретирован по типу view; узкие срезы используют явные include/exclude.
- [ ] Dynamic шаги используют существующие static relationships и последовательно пронумерованы.
- [ ] Deployment environment, nodes, infrastructure nodes, instances и groups отделены от logical model.
- [ ] Tags назначены до styles; themes, overrides и terminology не ломают семантику C4.
- [ ] `!include`, extension, `!docs` и `!adrs` используют безопасные относительные пути.
- [ ] Structurizr CLI validation выполнена либо fallback и ограничение явно отражены.
- [ ] Экспорт проверен, если его просили; синтаксис не выдан за архитектурную полноту.

## Полный справочник Structurizr DSL

Этот раздел нужен, когда задачи нельзя решить одним шаблоном. Используй его
как reference во время написания DSL. Синтаксис Structurizr DSL
чувствителен к порядку обработки и к области видимости, поэтому сначала
проверь правила языка, а затем копируй нужный фрагмент.

### 1. Лексические правила и структура файла

Structurizr DSL — императивный язык. Парсер читает файл сверху вниз и сразу
добавляет описанные сущности в workspace. Поэтому объект должен быть объявлен
до отношения, view, instance, include/exclude или другого выражения, которое
на него ссылается.

Базовая структура:

```dsl
workspace "Имя workspace" "Назначение workspace" {
    !identifiers hierarchical

    model {
        // элементы и отношения
    }

    views {
        // views, styles, themes и terminology
    }

    configuration {
        // scope, visibility, users и свойства workspace
    }
}
```

Правила разбора:

- перенос строки разделяет инструкции; длинную инструкцию можно продолжить,
  поставив `\` последним символом строки;
- количество пробелов и отступов не имеет значения, но токены должны быть
  разделены пробелами;
- ключевые слова нечувствительны к регистру, однако в проекте используй
  канонический стиль `softwareSystem`, `autoLayout`, `deploymentNode`;
- строки без пробелов можно писать без кавычек, но для описаний всегда
  используй кавычки;
- если нужно пропустить необязательный аргумент перед последующим аргументом,
  используй пустую строку `""`;
- открывающая `{` находится в той же строке, что и инструкция, которая её
  открывает; закрывающая `}` находится на отдельной строке;
- блоки без дочерних инструкций можно не открывать;
- комментарии бывают `# комментарий`, `// комментарий`, `/* комментарий */`
  и многострочные `/* ... */`;
- внутри строк используй DSL-экранирование кавычек и обратного слеша; не
  полагайся на особенности оболочки или Markdown.

Пример пропуска аргумента:

```dsl
container "API" "Обрабатывает запросы" "Kotlin/Ktor"
container "Без технологии" "Описание" ""
```

Имена и descriptions могут содержать Markdown. Не помещай в description
архитектурные факты, которые противоречат model или relationships: текст
диаграммы должен объяснять модель, а не маскировать её отсутствие.

### 2. Workspace, constants и переменные

`workspace` — корневой блок. Он может иметь имя и описание, свойства,
`model`, `views`, `configuration`, подключённые документы и ADR. Имя и описание
можно опустить:

```dsl
workspace {
    model { }
    views { }
}
```

Константы и переменные уменьшают повторение строк:

```dsl
!const ORGANISATION "Организация"
!const API_TECHNOLOGY "Kotlin/Ktor"
!var ENVIRONMENT "Development"

workspace "${ORGANISATION}" {
    model {
        api = softwareSystem "API" "Система организации" "Internal"
    }
}
```

Правила:

- `!const NAME value` задаёт постоянное значение;
- `!var NAME value` задаёт значение, которое можно переопределить позже;
- имя константы/переменной использует только `a-z`, `A-Z`, цифры, `-`, `_` и
  `.`;
- `${NAME}` подставляется внутри строк и может ссылаться также на переменную
  окружения;
- если значение не найдено, строка остаётся без подстановки; это нужно
  проверить, а не считать допустимым результатом;
- не используй переменные для скрытия важных архитектурных решений: итоговый
  DSL должен оставаться читаемым.

`properties` задаёт произвольные пары ключ-значение для workspace, элемента
или relationship:

```dsl
properties {
    "owner" "platform-team"
    "criticality" "high"
}
```

Для `properties` с одинаковым ключом определи, какое значение должно иметь
приоритет. Свойства можно использовать в expressions и в документации, но они
не заменяют tags: tags предназначены для фильтрации и стилей.

### 3. Идентификаторы и области видимости

Identifier появляется слева от `=`:

```dsl
user = person "Пользователь"
system = softwareSystem "Система"
system.api = container "API"
```

Обычные identifiers содержат только `a-z`, `A-Z`, цифры и `_`. Не используй
пробелы, дефисы и точки внутри одного сегмента. Точка разрешена как разделитель
в hierarchical scope.

В режиме flat каждый identifier должен быть уникален во всём workspace. В
сложной модели включи hierarchical mode в `workspace` до блока `model`:

```dsl
model {
    booking = softwareSystem "Бронирование" {
        api = container "API"
    }
    billing = softwareSystem "Оплата" {
        api = container "API"
    }

    booking.api -> billing.api "Передаёт платёжную заявку"
}
```

В hierarchical mode полные пути различают одинаковые локальные имена. Режим
не делает groups и relationship identifiers иерархическими. При ссылке на
элемент используй доступный в текущем scope identifier или полный путь.

`this` ссылается на текущий элемент вложенного блока:

```dsl
system = softwareSystem "Система" {
    api = container "API"
    db = container "База данных"
    api -> db "Читает данные"
}
```

Если связь объявляется в scope `api`, `this` может обозначать `api`:

```dsl
system = softwareSystem "Система" {
    api = container "API" {
        db = container "Локальное хранилище"
        this -> db "Читает"
    }
}
```

Используй явные identifiers для элементов, которые будут участвовать в
relationships, views, Dynamic, Deployment, expressions или документационных
ссылках. Не переименовывай identifier без поиска всех его употреблений.

### 4. Model и типы элементов

`model` обязателен. В нём можно объявлять `person`, `softwareSystem`,
`deploymentEnvironment`, custom `element`, `group`, archetypes, relationships и
операции над уже созданной моделью.

#### Person

```dsl
customer = person "Клиент" "Пользователь системы" "External"
```

Полная форма:

```dsl
customer = person "Клиент" "Пользователь" "External" {
    tags "Customer,Important"
    url "https://example.com/person/customer"
    properties {
        "role" "customer"
    }
    perspectives {
        "Security" "Uses MFA"
    }
}
```

Person получает системные tags `Element` и `Person`. Person моделирует роль,
персону или актора, а не конкретную HTTP-сессию, устройство или таблицу.

#### Software system

```dsl
booking = softwareSystem "Система бронирования" "Создаёт и отменяет бронирования" "Internal" {
    web = container "Web application" "Интерфейс пользователя" "Kotlin/React"
    api = container "API" "Принимает команды" "Kotlin/Ktor"
    db = container "Booking database" "Хранит бронирования" "PostgreSQL" {
        tags "Database"
    }

    web -> api "Отправляет запросы" "HTTPS/JSON"
    api -> db "Читает и изменяет бронирования" "SQL"
}
```

Software system получает tags `Element` и `Software System`. Внутри него
разрешены containers, groups, relationships, properties, URL, perspectives,
`!docs` и `!adrs`.

#### Container

Container — логически самостоятельная часть software system: приложение,
сервис, база данных, очередь, файл или другой исполняемый/развёртываемый блок.
Это не обязательно Docker container.

```dsl
api = container "API" "Принимает запросы и возвращает ответы" "Kotlin/Ktor" {
    auth = component "Authentication" "Проверяет пользователя" "Kotlin"
    booking = component "Booking service" "Управляет бронированиями" "Kotlin"
}
```

Container получает tags `Element` и `Container`. Technology должна описывать
реальную технологию или форму исполнения, если она известна; не подставляй
модный стек без источника.

#### Component

Component объявляется только внутри container:

```dsl
bookingController = component "Booking controller" "Принимает команды бронирования" "Ktor routing"
bookingService = component "Booking service" "Проверяет правила бронирования" "Kotlin"
bookingRepository = component "Booking repository" "Работает с хранилищем" "Exposed"

bookingController -> bookingService "Передаёт команду"
bookingService -> bookingRepository "Сохраняет бронирование"
```

Component получает tags `Element` и `Component`. Не создавай Component view,
если внутренние части контейнера неизвестны: C4 не требует придумывать детали.

#### Custom element и archetypes

`element` позволяет добавить тип, которого нет среди базовых C4-элементов:

```dsl
queue = element "Message broker" true "Передаёт сообщения" "Queue" {
    technology "RabbitMQ"
}
```

Custom element используй только для понятной архитектурной сущности, которую
нельзя выразить software system, container, component или infrastructure node.
Обязательно добавь custom tag и объясни выбор в документации.

Archetype задаёт переиспользуемый тип с defaults для description, technology,
tags, properties и perspectives. Сначала проверь официальную страницу
Archetypes и только затем вводи его в общий workspace: archetypes усложняют
модель и должны экономить заметное дублирование.

#### Group

Groups рисуют границы вокруг элементов одного уровня:

```dsl
group "Внутренние команды" {
    platform = softwareSystem "Platform"
    booking = softwareSystem "Booking"
}
```

Разрешённые уровни:

| Scope | Что можно группировать |
| --- | --- |
| `model` | `person` и `softwareSystem` |
| `softwareSystem` | `container` |
| `container` | `component` |

Не используй group как замену границе software system или deployment node.
Для отдельного component можно задать group через `group "Имя"` внутри его
блока.

#### Общие свойства элементов

Для элемента доступны `description`, `tags`, `url`, `properties`,
`perspectives` и отношения; `technology` задаётся для containers, components,
deployment nodes и infrastructure nodes. `instances` задаёт количество
экземпляров deployment node. Технология и description должны быть разными
полями: technology — чем реализовано, description — какую функцию выполняет.

### 5. Relationships

Базовый синтаксис:

```dsl
source -> destination "Описание действия" "Технология" "Tag1,Tag2" {
    properties {
        "protocol" "HTTPS"
    }
}
```

Description и technology можно опустить или пропустить через `""`. Relationship
однонаправленный; для двустороннего взаимодействия создай две связи:

```dsl
client -> api "Отправляет запрос" "HTTPS"
api -> client "Возвращает ответ" "HTTPS/JSON"
```

Ограничения:

- source и destination должны быть уже объявлены;
- между одной парой source/destination descriptions должны различаться;
- направление отражает зависимость или поток вызова, а не расположение на
  рисунке;
- description начинается с действия и отвечает на вопрос «что происходит»;
- technology указывай только если она подтверждена и полезна читателю;
- не используй relation как декоративную линию;
- tag `Relationship` добавляется автоматически; добавляй дополнительные tags
  для фильтров, стилей и семантических срезов;
- relationship identifier нужен, когда связь будет адресоваться явно, например
  в Dynamic или `!relationship`.

Именованная relationship:

```dsl
request = client -> api "Отправляет запрос" "HTTPS"
```

В Dynamic view можно использовать существующую relationship и изменить только
контекстное описание шага. Статическая модель остаётся источником допустимых
связей.

#### Implied relationships

По умолчанию Structurizr может вывести связь между родительскими элементами,
если есть связь между вложенными элементами. Например, `person -> container`
может породить `person -> softwareSystem`. Это удобно для верхних views, но
может скрыть ошибку в границах.

```dsl
!impliedRelationships false
```

Отключай implied relationships, когда модель должна содержать только явно
утверждённые контракты. Значение `true` включает стандартную стратегию. В
расширенных сценариях может быть указан fully qualified class name стратегии;
не добавляй такую зависимость без проверки версии парсера.

После изменения этого параметра заново проверь состав `include *` всех views:
implied relationships влияют на видимые связи, но не должны использоваться для
компенсации отсутствующих исходных relationships.

#### Удаление relationship

При расширении workspace или повторном использовании базовой модели можно
удалить relationship специальной операцией `!relationship`, если это явно
поддерживается целевой версией DSL. Перед применением открой language reference
для этой версии и проверь точную форму: операции удаления чувствительны к
identifier/описанию связи.

### 6. Операции над моделью и bulk expressions

DSL поддерживает операции, которые применяются к уже созданным сущностям:

- `!ref` получает ссылку на существующий элемент;
- `!element` и `!elements` применяют операцию к одному или нескольким
  элементам;
- `!relationship` и `!relationships` применяют операцию к отношениям;
- `description`, `technology`, `tags`, `url`, `properties`, `perspectives` и
  `instances` могут использоваться внутри соответствующей области.

Для bulk операций используй expressions из следующего раздела. Любая массовая
операция должна иметь проверяемый scope: сначала выполни выражение мысленно на
малой модели и убедись, что оно не затронет лишние элементы.

### 7. Expressions для include/exclude и bulk operations

Expression в кавычках, если внутри есть пробел:

```dsl
include "element.tag==Public API"
exclude "element.type==Database"
```

#### Element expressions

| Expression | Смысл |
| --- | --- |
| `->id` | элемент и входящие связи |
| `id->` | элемент и исходящие связи |
| `->id->` | элемент и входящие/исходящие связи |
| `element.type==Container` | элементы указанного типа |
| `element.parent==id` | элементы с указанным родителем |
| `element.tag==Tag` | элементы со всеми указанными tags |
| `element.tag!=Tag` | элементы без указанного набора tags |
| `element.technology==Kotlin` | элементы с technology |
| `element.technology!=Kotlin` | элементы с другой/пустой technology |
| `element.properties[name]==value` | элементы с property и значением |
| `element.group==name` | элементы указанной группы |
| `element==->id` | element/group и входящие связи |
| `element==id->` | element/group и исходящие связи |
| `element==->id->` | element/group и все связи |

#### Relationship expressions

| Expression | Смысл |
| --- | --- |
| `*->*` или `relationship==*` | все relationships |
| `id->*` | отношения с указанным source |
| `*->id` | отношения с указанным destination |
| `relationship.tag==Tag` | relationships со всеми указанными tags |
| `relationship.tag!=Tag` | relationships без указанного набора tags |
| `relationship.properties[name]==value` | relationships с property |
| `relationship.source==id` | relationships от source |
| `relationship.destination==id` | relationships к destination |
| `relationship==id->*` | отношения от source |
| `relationship==*->id` | отношения к destination |
| `relationship==id->id` | отношения между двумя элементами |

Expressions можно объединять `&&` и `||`:

```dsl
include "element.type==Container && element.parent==booking"
exclude "relationship.tag==Internal || relationship.properties[deprecated]==true"
```

Сначала проверяй сложное выражение на маленьком примере. Для очень сложной
логики используй DSL script/plugin только после оценки поддержки среды.

### 8. Views: общие правила

`views` содержит views, keys, title, description, includes/excludes, layout,
animation и styles. View не создаёт элементов: она выбирает уже существующую
часть model.

Указывай стабильный ключ:

```dsl
systemContext booking "BookingSystemContext" {
    title "Контекст системы бронирования"
    description "Кто и какие системы взаимодействуют с бронированием"
    include *
    autoLayout lr
}
```

Автоматически сгенерированный key может измениться и привести к потере ручного
layout. Каждая view должна иметь уникальный key в workspace.

Общие view-инструкции:

- `include` добавляет элементы и связанные отношения по scope;
- `exclude` убирает элементы/отношения после включения;
- включение relationship само по себе не добавляет отсутствующие элементы;
- view должна иметь достаточно узкую цель, чтобы её можно было прочитать;
- `autoLayout` задавай после include/exclude;
- `default` управляет стилями/метаданными по умолчанию для конкретной view;
- `animation` разбивает большой сценарий или структуру на последовательные
  группы; используй только когда шаги действительно полезны;
- `title` и `description` объясняют цель view и не дублируют все labels.

### 9. System Landscape view

Показывает людей и software systems в широком контексте:

```dsl
systemLandscape "Landscape" {
    include *
    autoLayout lr
}
```

Используй явные include, если workspace содержит несколько независимых
областей:

```dsl
systemLandscape "PublicLandscape" {
    include customer
    include booking
    include payment
    include customer -> booking
    include booking -> payment
    autoLayout lr
}
```

Не помещай containers и components в landscape без специально обоснованной
нестандартной view.

### 10. System Context view

Показывает одну software system и внешних людей/систем, которые с ней
взаимодействуют:

```dsl
systemContext booking "BookingContext" {
    include *
    autoLayout lr
}
```

Если нужны только связи к системе, используй `*?` или явные relationships,
когда это поддерживается целевой версией. Проверяй результат: контекстная view
не должна случайно раскрыть внутренние containers.

### 11. Container view

Показывает containers выбранной software system и внешнее окружение:

```dsl
container booking "BookingContainers" {
    include *
    autoLayout lr
}
```

Явный срез:

```dsl
container booking "PublicApi" {
    include booking.api
    include booking.db
    include customer
    include customer -> booking.api
    include booking.api -> booking.db
    autoLayout lr
}
```

Не называй внутренний сервис «системой» только ради удобства container view.
Если сервис является самостоятельной системой с отдельным владельцем и
границей, это нужно доказать моделью и контекстом.

### 12. Component view

Показывает components одного container:

```dsl
component booking.api "BookingApiComponents" {
    include *
    autoLayout lr
}
```

Component view может включить внешние элементы, от которых зависят components,
но не должна превращаться в полный Container view. Components должны иметь
реальные ответственности, а не соответствовать каждой строке кода, классу или
методу.

### 13. Dynamic view

Dynamic view принимает `*`, software system или container как scope и описывает
упорядоченный сценарий:

```dsl
dynamic booking "CreateBooking" {
    title "Создание бронирования"
    customer -> booking.web "Открывает форму" "HTTPS" 1
    booking.web -> booking.api "Отправляет заявку" "HTTPS/JSON" 2
    booking.api -> booking.db "Сохраняет заявку" "SQL" 3
    booking.api -> customer "Возвращает подтверждение" "HTTPS/JSON" 4
    autoLayout lr
}
```

Точная форма аргументов может включать relationship identifier и номер шага;
проверь её по language reference версии CLI. Смысл остаётся постоянным:

- шаги используют пару элементов и существующую static relationship;
- номер задаёт порядок и может быть десятичным для вставки шага между двумя
  существующими шагами, если это поддерживает версия parser;
- описание шага может быть контекстнее статического description;
- один dynamic view описывает один use case, feature или story;
- для параллельных последовательностей используй официальную форму parallel
  sequences и явно объясни границы параллелизма;
- Dynamic view не заменяет статические Container/Component views.

Перед проверкой Dynamic составь таблицу `шаг -> source -> destination -> static
relationship`. Любая строка без static relationship — ошибка модели, а не
только ошибка оформления.

### 14. Deployment model и Deployment view

Deployment model описывает экземпляры логических элементов в runtime:

```dsl
model {
    api = softwareSystem "Booking" {
        service = container "API" "Принимает запросы" "Kotlin/Ktor"
    }

    production = deploymentEnvironment "Production" {
        cluster = deploymentNode "Kubernetes cluster" "Исполняет workloads" "Kubernetes" {
            pod = deploymentNode "Booking namespace" {
                serviceInstance = containerInstance api.service
            }
        }
        database = infrastructureNode "PostgreSQL" "Хранит данные" "PostgreSQL"
        cluster -> database "Подключается к базе" "TCP/5432"
    }
}

views {
    deployment api "ProductionDeployment" "Production" {
        include *
        autoLayout lr
    }
}
```

Типы Deployment:

- `deploymentEnvironment` — Development, Test, Staging, Production или другое
  runtime-окружение;
- `deploymentNode` — host, VM, cluster, namespace, process boundary или
  платформа; nodes можно вкладывать;
- `infrastructureNode` — load balancer, firewall, DNS, broker, database service
  или другой инфраструктурный объект;
- `softwareSystemInstance` — экземпляр software system на node;
- `containerInstance` — экземпляр container на node;
- `deploymentGroup` — группа связанных экземпляров внутри node;
- `instanceOf` — сокращение для создания instance; используй его только если
  результат очевиден и валиден для версии DSL;
- `healthCheck` — проверка доступности/состояния deployment instance или
  infrastructure node; задавай URL, имя и timeout по синтаксису текущей версии.

Пример группы и нескольких экземпляров:

```dsl
production = deploymentEnvironment "Production" {
    nodes = deploymentNode "Application nodes" {
        deploymentGroup "Booking API replicas" {
            api1 = containerInstance api.service
            api2 = containerInstance api.service
        }
    }
}
```

Deployment relationships описывают runtime connectivity. Не считай их заменой
логических relationships: обе модели могут быть необходимы и должны быть
согласованы.

### 15. Filtered view

Filtered view строится поверх существующей base view:

```dsl
filtered "BookingContainers" "SecurityOnly" include "Security"
```

Или исключает tag:

```dsl
filtered "BookingContainers" "WithoutInternal" exclude "Internal"
```

Правила:

- base view должна существовать и иметь стабильный key;
- фильтр работает по tags элементов и relationships;
- filtered view не является новой model и не добавляет elements;
- в некоторых renderer базовая view скрывается из списка после создания
  filtered view; если нужны обе, включи `Element,Relationship` согласно
  официальной форме filtered view;
- проверяй, что tag назначен до создания view и что фильтр не скрывает
  обязательную границу.

### 16. Custom view

Custom view предназначена для нестандартного arrangement custom elements и
relationships, когда обычная C4 view не выражает нужную структуру:

```dsl
custom "IntegrationLandscape" "CustomIntegration" {
    include queue
    include queue -> booking.api
    autoLayout lr
}
```

Custom view не должна становиться способом обойти корректное моделирование
software systems, containers или components. В language reference проверь,
какие элементы разрешены для выбранной версии и renderer.

### 17. Image view

Image view связывает C4 workspace с заранее подготовленным изображением или
внешним языком диаграмм:

```dsl
image "Level4" "ComponentDetail" {
    image "images/booking-component.png"
}
```

Точная форма зависит от источника и версии. Перед использованием проверь:

- путь к локальному файлу и его существование;
- MIME/формат изображения;
- доступность HTTPS-ресурса, если используется URL;
- приватность: внешний PlantUML/Mermaid/Kroki сервис может получить содержимое
  диаграммы;
- переносимость и наличие изображения в Git;
- что image view не скрывает основную C4 model.

### 18. Include, exclude и `include *`

Общие формы:

```dsl
include *
include *?
include booking.api
include customer -> booking.api
include "element.tag==Public"
exclude booking.internal
exclude "relationship.tag==Deprecated"
```

`include *` означает scoped wildcard, а не все элементы workspace:

| View | Обычный scoped результат |
| --- | --- |
| `systemLandscape` | все people и software systems |
| `systemContext system` | system и связанные внешние people/systems |
| `container system` | containers system и внешнее окружение |
| `component container` | components container и нужное окружение |
| `deployment ... environment` | deployment nodes, infrastructure и instances |
| `dynamic` | не используется для выбора static состава |

`*?` — reluctant wildcard для поддерживаемых контекстных views: он выбирает
scoped элементы, но ограничивает автоматически добавляемые relationships до
связей со scope. Не применяй его по памяти к Dynamic или Deployment: проверь
семантику целевой версии.

Порядок безопасной настройки view:

1. выбери scope;
2. включи минимальный набор элементов;
3. включи необходимые relationships или expressions;
4. исключи шум;
5. выполни auto layout;
6. проверь итоговый состав в renderer/export.

### 19. Styles и tags

Tags — семантическая метка элемента или relationship. Styles сопоставляются с
tags:

```dsl
views {
    styles {
        element "Element" {
            color #ffffff
            fontSize 24
        }
        element "Person" {
            shape Person
            background #084c61
        }
        element "Database" {
            shape Cylinder
            background #5c946e
        }
        relationship "Relationship" {
            color #555555
            thickness 2
            fontSize 16
        }
    }
}
```

Element style может задавать `shape`, `icon`, `width`, `height`, `background`,
`color`, `stroke`, `fontSize`, `border`, `opacity`, `metadata` и отображение
description. Relationship style может задавать `thickness`, `color`, `style`,
`routing`, `jump`, `fontSize`, `width`, `position` и `opacity`. Точная поддержка
свойств зависит от renderer.

Правила стилей:

- сначала назначь tags, затем styles;
- базовые tags `Element`, `Person`, `Software System`, `Container`, `Component`
  и `Relationship` можно переопределять, но делай это осознанно;
- tag names с пробелами заключай в кавычки;
- не кодируй критическую семантику только цветом;
- не используй десятки почти одинаковых tags;
- сохраняй читаемость в чёрно-белом и экспортированном виде;
- локальные styles workspace могут переопределить theme styles;
- иконки и нестандартные shapes нужно проверить в каждом требуемом формате.

`light` и `dark` позволяют задавать варианты стилей для светлой и тёмной темы,
если renderer поддерживает их:

```dsl
styles {
    light {
        element "Database" { background #e8f5e9 }
    }
    dark {
        element "Database" { background #1b5e20 }
    }
}
```

### 20. Themes и terminology

Theme — JSON-набор tag-based styles. Подключение может быть по имени, локальному
файлу или HTTPS URL:

```dsl
views {
    theme default
    theme "https://example.com/structurizr-theme.json"
    themes "themes/company.json", "themes/cloud.json"
}
```

Для remote theme проверь доступность, версию, безопасность и воспроизводимость.
Предпочитай локально закреплённый theme, когда диаграмма должна собираться в
CI без сети. После подключения theme проверь, что model elements имеют нужные
tags.

`terminology` меняет отображаемые подписи терминов, но не семантику C4:

```dsl
terminology {
    person "Пользователь"
    softwareSystem "Система"
    container "Сервис или хранилище"
    component "Компонент"
    relationship "Связь"
}
```

Не называй container «системой» в terminology, если это стирает архитектурный
уровень. Server-level CSS/JavaScript customization — отдельный механизм и не
является частью DSL.

### 21. Perspectives, URLs, instances и health checks

Perspectives позволяют добавить дополнительный взгляд на element или
relationship: например Security, Performance, Cost или Availability.

```dsl
api = container "API" "Обрабатывает запросы" "Kotlin/Ktor" {
    perspectives {
        "Security" "Requires authentication"
        "Availability" "Runs in two replicas"
    }
}
```

Используй perspectives для контекстной оценки, а не для хранения основной
description. `url` добавляет ссылку на внешний источник, repository или
документацию:

```dsl
api url "https://github.com/example/booking-api"
```

`instances` и `healthCheck` применяй в Deployment-модели, когда нужно показать
runtime cardinality и операционное состояние. Не выдавай число instances за
гарантию отказоустойчивости без описания распределения и health policy.

### 22. Документация и ADR

`!docs` подключает Markdown/AsciiDoc к workspace, software system или
container:

```dsl
workspace "Booking" {
    !docs docs/architecture
    model {
        booking = softwareSystem "Booking" {
            !docs docs/booking
        }
    }
}
```

Обычно импортируются документы из указанного каталога и вложенных каталогов в
определённом порядке. Сверь поддержку Markdown, AsciiDoc, изображений и
необязательного fully qualified class name с официальной документацией.

`!adrs` подключает Architecture Decision Records:

```dsl
workspace "Booking" {
    !adrs decisions/adr madr
}
```

Проверь формат ADR (`adrtools`, `madr`, `log4brains` или поддерживаемый
пользовательский формат), порядок файлов и связь записи с нужным элементом.
Документы и ADR дополняют model; они не должны быть единственным местом, где
описаны обязательные элементы и relationships.

### 23. !include и workspace extension

`!include` вставляет DSL-фрагмент в место вызова:

```dsl
workspace "Booking" {
    model {
        !include model/people.dsl
        !include model/systems.dsl
        !include model/relationships.dsl
    }
    views {
        !include views/booking.dsl
    }
}
```

Правила модульности:

- локальный путь должен быть relative к parent DSL file или находиться в его
  subdirectory;
- directory include обрабатывает допустимые файлы в порядке, который нужно
  считать частью проверки;
- подключаемый фрагмент обязан попадать в правильный scope (`model` или
  `views`);
- объявляй элементы и relationships до фрагментов, которые на них ссылаются;
- не используй непроверенные абсолютные пути и пути за пределами рабочего
  дерева;
- HTTPS include применяй только для доверенного одиночного DSL-файла и
  учитывай сетевую недоступность.

Workspace extension расширяет другой workspace:

```dsl
workspace extends "base-workspace.dsl" {
    model {
        extra = softwareSystem "Дополнительная система"
    }
    views {
        systemLandscape "ExtendedLandscape" {
            include *
        }
    }
}
```

Base workspace может быть локальным DSL/JSON или HTTPS URL. При расширении DSL
его identifiers доступны в дочернем workspace. До изменения extension проверь,
какие views, styles, properties и relationships уже определены, и не создавай
конфликты ключей.

### 24. Scripts и plugins

`!script` подключает скрипт для программного изменения workspace, а `!plugin`
подключает plugin. Такие механизмы имеют более высокий риск и меньшую
переносимость, чем обычный DSL:

- применяй их, только если обычные конструкции не выражают требование;
- прочитай официальную документацию по sandbox, языку, API и версии;
- проверь, не выполняется ли код с доступом к сети или файловой системе;
- закрепи зависимости и результаты в CI;
- не прячь в script критическую model-логику, которую должен читать reviewer;
- plugins для PlantUML/Mermaid требуют проверки внешнего renderer и экспортных
  ограничений.

### 25. Configuration

`configuration` задаёт параметры workspace, не являющиеся model elements:

```dsl
configuration {
    scope softwaresystem
    visibility private
    users {
        "architect@example.com" readwrite
    }
    properties {
        "title" "Architecture workspace"
    }
}
```

Точные значения `scope`, `visibility` и права пользователей зависят от
Structurizr Server/Cloud и версии DSL. Не добавляй credentials, tokens или
секреты в DSL. Для публичного workspace проверь, не раскрывают ли descriptions,
URLs, documentation и ADR внутреннюю информацию.

### 26. Defaults

Defaults позволяют задать общие значения для создаваемых элементов и views.
Используй их для повторяемого оформления, но оставляй исключения явными. Если
default и локальный параметр конфликтуют, проверь фактический приоритет через
CLI или минимальный воспроизводимый workspace.

### 27. Export и среды выполнения

Structurizr DSL workspace может быть обработан playground, Structurizr Lite,
local, server/on-premises окружением или CLI. Это разные среды с разными
ограничениями.

Основные CLI-операции:

```bash
structurizr validate -workspace workspace.dsl
structurizr export -workspace workspace.dsl -format plantuml
structurizr export -workspace workspace.dsl -format mermaid
```

Перед запуском сверяй `structurizr --help`: расположение аргументов и список
форматов меняются между версиями.

`validate` проверяет DSL/model, но не доказывает, что диаграмма полезна человеку.
`export` создаёт представления в выбранном формате; после него проверь:

- создан ли файл для каждой ожидаемой view;
- присутствуют ли ключевые элементы, labels и relationships;
- не исчезли ли shapes, icons, colors, themes, metadata и layout;
- не появились ли неожиданные relations из-за implied relationships;
- не передаётся ли конфиденциальная модель внешнему сервису.

Mermaid, PlantUML, WebSequenceDiagrams, SVG, PNG, JSON и static HTML имеют
разную полноту поддержки. Валидность в Structurizr не равна идентичному
визуальному результату во всех экспортерах.

### 28. Полный протокол работы агента

Используй этот протокол для каждой задачи, даже если изменение кажется малым:

1. Запиши цель, читателя, границу системы, уровень C4 и требуемый output.
2. Найди существующий workspace, его keys, identifiers, tags, includes и
   документацию.
3. Определи, какие факты известны, какие выведены из кода, а какие требуют
   подтверждения. Неподтверждённые детали обозначь в description или отчёте.
4. Составь model inventory: people, systems, containers, components,
   environments, nodes, instances и relationships.
5. Проверь вложенность и уникальность имён.
6. Выбери стабильные identifiers и реши, нужен ли hierarchical scope.
7. Объяви model сверху вниз: родители, дочерние элементы, static relationships,
   deployment topology и дополнительные properties/tags.
8. Для Dynamic составь таблицу соответствия каждому static relationship.
9. Создай views с явными keys, минимальным include/exclude и auto layout.
10. Подключи styles, themes, terminology, docs и ADR только после проверки
    структуры model.
11. Запусти `validate`, затем нужный `export`; при отсутствии CLI выполни
    fallback-проверки и укажи ограничение.
12. Проведи semantic review: уровни C4 не смешаны, границы честны, каждая
    стрелка объяснима, view отвечает своей аудитории.
13. Проверь diff, ссылки, пути, generated artifacts и совместимость с локальными
    соглашениями репозитория.

Критерий полного результата: другой агент может открыть DSL, понять модель без
устного пояснения, воспроизвести проверку и определить, какие утверждения
являются фактами, а какие — явно отмеченными допущениями.

### 29. Сводка официальных разделов для дальнейшего чтения

При version-sensitive вопросе переходи к соответствующему первичному разделу,
а не угадывай синтаксис:

- [Basics](https://docs.structurizr.com/dsl/basics) — правила строк,
  комментарии, константы и подстановки;
- [Language reference](https://docs.structurizr.com/dsl/language) — полный
  синтаксис workspace, model, elements, relationships, views, styles и
  configuration;
- [Identifiers](https://docs.structurizr.com/dsl/identifiers) — flat/hierarchical
  scope и ограничения имён;
- [Archetypes](https://docs.structurizr.com/dsl/archetypes) — пользовательские
  типы элементов и relationships;
- `basics` — правила строк, комментарии, константы и подстановки;
- `language` — полный синтаксис workspace, model, elements, relationships,
  views, styles и configuration;
- `identifiers` — flat/hierarchical scope и ограничения имён;
- `archetypes` — пользовательские типы элементов и relationships;
- `implied-relationships` — стратегия вывода родительских связей;
- `expressions` — выборка элементов и relationships;
- `includes` и `workspace-extension` — модульность и наследование workspace;
- `docs` и `adrs` — подключение документации и решений;
- `scripts` и `plugins` — программные расширения и внешние renderer;
- `cookbook` — минимальные рабочие примеры по каждому виду view;
- `patterns` — официальные архитектурные заготовки;
- `validate`, `export`, `local`, `lite`, `server` — проверка и запуск;
- `faq` — ограничения parser и причины неоднозначного поведения.

Полный список ссылок и краткие выводы уже собраны в локальной
[исследовательской заметке](../diagrams/structurizr-dsl-for-agents-research.md).
При расхождении этого справочника с установленной версией Structurizr
приоритет имеют `--help`, фактический результат CLI и официальная документация
этой версии. Зафиксируй обнаруженное расхождение в итоговом отчёте и обнови
локальную инструкцию отдельным изменением.
