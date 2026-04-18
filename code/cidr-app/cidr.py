# -------- CIDR TOOL --------
@app.route('/cidr')
def cidr_page():
    auth = check_auth()
    if auth:
        return auth

    r = requests.get(f"{CIDR_SERVICE}/")
    return Response(r.content, r.status_code)


@app.route('/cidr/calculate', methods=['POST'])
def cidr_calculate():
    auth = check_auth()
    if auth:
        return auth

    r = requests.post(
        f"{CIDR_SERVICE}/",
        data=request.form
    )

    return Response(r.content, r.status_code)