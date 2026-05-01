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
#include "sections/intro.typ"

#pagebreak()
#include "sections/environment.typ"

#pagebreak()
#include "sections/architecture.typ"

#pagebreak()
#include "sections/steps.typ"

#pagebreak()
#include "sections/questions.typ"
