#import "conf.typ": template

#show: template

#include "sections/title.typ"
#pagebreak()

#include "sections/abstract.typ"
#pagebreak()

#heading(numbering: none)[Содержание]
#outline(
    title: none,
)

#pagebreak()

#include "sections/architecture.typ"
#include "sections/steps.typ"
