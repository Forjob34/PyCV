data = {
    "radiator_type": {
        "type": "",
        "sizes": {
            "height": 50.0,
            "lenght": 50.0
        }
    }
}
res = {}
for i in data["radiator_type"]['sizes']:
    print(i[0])
    print(i.values())
