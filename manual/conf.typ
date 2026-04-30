#import "constants.typ": color

#let template(body) = {
    set document(
        author: "Иван Скребцов",
    )

    set page(
        paper: "a4",
        header: context {
            set text(size: 10pt, fill: color.grey)
            set par(spacing: 0.5em, first-line-indent: 0cm)

            [Методическое пособие]
            h(1fr)
            counter(page).display("1")
            line(length: 100%, stroke: color.grey + 0.3pt)
        },
        footer: {
            set par(spacing: 0.5em, first-line-indent: 0cm)
            set text(size: 10pt, fill: color.grey)
            set align(left)

            line(length: 100%, stroke: color.grey + 0.3pt)
            [Специальность 09.02.08 — Интеллектуальные Интегрированные Системы]
        },
    )

    set par(
        first-line-indent: (amount: 1.7cm, all: true),
        justify: true,
        leading: 0.75em,
        spacing: 0.75em,
    )

    set text(
        font: "Times New Roman",
        size: 12pt,
        top-edge: "ascender",
        bottom-edge: "descender",
        lang: "ru",
    )

    // Headings
    set heading(numbering: "1.")

    show heading: set text(size: 12pt)
    show heading.where(level: 1): it => block(width: 100%)[
        #set align(center)
        #set text(size: 14pt)
        #it
        #v(-1em)
        #line(length: 100%, stroke: color.black + 0.3pt)
    ]

    // Outline
    show outline.entry: it => {
        link(
            it.element.location(),
            it.indented(it.prefix(), [#it.body() #h(1fr) #it.page()]),
        )
    }

    // Lists
    set list(
        marker: [•],
        indent: 1.7cm,
    )

    // Code
    show raw.where(block: false): body => {
        box(
            fill: luma(245),
            inset: (x: 3pt, y: 0pt),
            outset: (y: 3pt),
            radius: 2pt,
        )[
            #set text(font: "Courier New")
            #body
        ]
    }
    show raw.where(block: true): body => {
        block(fill: luma(245), radius: 2pt, width: 90%, inset: (
            x: 12pt,
            y: 8pt,
        ))[
            #set align(left)
            #set text(font: "Courier New")
            #body
            #align(right)[#body.lang]
        ]
    }

    body
}
