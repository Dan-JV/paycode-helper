def create_yaml_object(paycode: dict, form_template: dict) -> dict:
    """
    This function takes a paycode (dict) and a form template (dict) and returns a yaml object that can be used to generate a form.
    """
    
    for area in form_template["areas"]:
        if area["name"] == "Catalog Input":
            for i, field in enumerate(area["fields"]):
                if field["catalog_name"] in paycode:
                    area["fields"][i]["input"] = paycode[
                        field["catalog_name"]
                    ][0]
    return form_template





