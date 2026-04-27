from flask import Flask, render_template, request
import ipaddress

app = Flask(__name__)

OCTET_CLASSES = ["o1", "o2", "o3", "o4"]

def ip_to_binary(ip):
    return "".join([format(int(o), "08b") for o in ip.split(".")])

@app.route("/", methods=["GET", "POST"])
def index():
    data = None
    error = None

    if request.method == "POST":
        cidr = request.form.get("cidr")

        try:
            net = ipaddress.ip_network(cidr.strip(), strict=False)

            ip_bin = ip_to_binary(str(net.network_address))
            prefix = net.prefixlen

            bits = []
            for i, bit in enumerate(ip_bin):
                octet_index = i // 8
                bits.append({
                    "bit": bit,
                    "octet_class": OCTET_CLASSES[octet_index],
                    "type": "network" if i < prefix else "host"
                })

            # split into octets
            octets = [bits[i:i+8] for i in range(0, 32, 8)]

            # usable
            if net.num_addresses > 2:
                first_ip = net.network_address + 1
                last_ip = net.broadcast_address - 1
                gateway = first_ip
            else:
                first_ip = last_ip = gateway = None

            data = {
                "octets_ip": str(net.network_address).split("."),
                "prefix": prefix,
                "bit_octets": octets,
                "network": str(net.network_address),
                "broadcast": str(net.broadcast_address),
                "first_ip": str(first_ip) if first_ip else "N/A",
                "last_ip": str(last_ip) if last_ip else "N/A",
                "gateway": str(gateway) if gateway else "N/A",
                "total_ips": net.num_addresses,
                "netmask": str(net.netmask)
            }

        except:
            error = "Invalid CIDR"

    return render_template("index.html", data=data, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5008)
