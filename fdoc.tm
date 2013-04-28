\define{funcdoc}\strip[
    \ul[
        \body
    ]
]

\define{field}\strip[
    \b[\[ \body \]]
]

\define{desc}\strip[
    \li[\field[解說] \body]
]

\define{params}\strip[
    \li[\field[引數]
        \ul\strip[
            \body
        ]
    ]
]

\define{param(name; type:str,'')}\strip[
    \li\strip[\i[\name]: 
        \body
        \ifval{\type}[(\c[\type] 型)]
    ]
]

