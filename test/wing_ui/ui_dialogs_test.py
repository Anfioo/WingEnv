from prompt_toolkit import HTML, print_formatted_text

print_formatted_text(
        HTML(
            '<style fg="#ff0066">hello</style> '
            '<style fg="#44ff44"><i>world</i></style>\n'
        )
    )

from prompt_toolkit import HTML, print_formatted_text

print_formatted_text(
        HTML(
            '<style fg="#ff0066">#</style> '
            '<style fg="#44ff44">#</style>\n'
        )
    )