#import "constants.typ": color

#let template(body) = {
    set text(
        font: "Times New Roman",
        size: 12pt,
        top-edge: "ascender",
        bottom-edge: "descender",
    )
    set page(
        paper: "a4",
        header: context {
            set text(size: 10pt, fill: color.grey)
            set par(spacing: 0.2em)

            [Методическое пособие]
            h(1fr)
            counter(page).display("1")
            line(length: 100%, stroke: color.grey + 0.3pt)
        },
        footer: {
            set par(spacing: 0.5em)
            set text(size: 10pt, fill: color.grey)
            set align(left)

            line(length: 100%, stroke: color.grey + 0.3pt)
            [Специальность 09.02.08 — Интеллектуальные Интегрированные Системы]
        },
    )

    show heading.where(level: 1): it => {
        block(width: 100%)[
            #set align(center)
            #set text(size: 14pt)
            #it.body
        ]
        v(-1em)
        line(length: 100%, stroke: color.black + 0.3pt)
    }

    body
}
