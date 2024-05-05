import requests
import pandas as pd
from jinja2 import Template
import os

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def fetch_user_data(url):
    try:
        response = requests.get(f"https://{url}/wp-json/wp/v2/users/")
        response.raise_for_status()
        users = response.json()
        return [{
            "domain": url,
            "id": user["id"],
            "name": user["name"],
            "url": user.get("url", ""),
            "description": user.get("description", ""),
            "slug": user.get("slug", ""),
            "slug_link": user.get("link", ""),
            "avatar_urls_24": user.get("avatar_urls", {}).get("24", "-"),
            "avatar_urls_48": user.get("avatar_urls", {}).get("48", "-"),
            "avatar_urls_96": user.get("avatar_urls", {}).get("96", "-"),
        } for user in users], len(users)
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return [], 0

def main():
    # Check and create reports folder
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    # Read file Domains
    with open("domains.txt", "r") as file:
        urls = [line.strip() for line in file.readlines()]

    all_users = []
    user_counts = {}
    for url in urls:
        users_data, count = fetch_user_data(url)
        all_users.extend(users_data)
        user_counts[url] = count

        # Generate CSV for each domain
        df_domain = pd.DataFrame(users_data)
        df_domain.to_csv(f"reports/{url.replace('://', '_').replace('/', '_')}.csv", sep=';', index=False)

    # Using pandas to create a general DataFrame
    df = pd.DataFrame(all_users)
    counts_df = pd.DataFrame(list(user_counts.items()), columns=["Domains", "Total Users"])

    # Export all data to a single CSV file
    df.to_csv("reports/wur-report.csv", sep=';', index=False)
    
    # Using Jinja2 to generate the HTML
    template_html = """
    <!DOCTYPE html>
    <!-- Author: Marcos Henrique -->
    <!-- GitHub: https://github.com/100security/wur -->
    <!-- Site: https://www.100security.com.br/wur -->
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
        <title>WP Users Report</title>
    </head>
    <body>
        <div class="container mt-4">
            <h1 class="mb-4"><center><i class="bi-people-fill"></i> WP Users Report</center></h1>
            <div class="panel mb-4">
                <table class="table table-hover table-bordered">
                    <thead class="table-dark text-center">
                        <tr>
                            <th class="text-center"><i class="bi-globe-americas"></i> Domains</th>
                            <th class="text-center"><i class="bi-person-fill"></i> Total Users</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in counts %}
                        <tr>
                            <td class="text-center"><a href="https://{{ item.Domains }}/wp-json/wp/v2/users/" target="_blank">{{ item.Domains }}</a></td>
                            <td class="text-center">{{ item['Total Users'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <table class="table table-hover table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th class="text-center">Domain</th>
                        <th class="text-center">Name</th>
                        <th class="text-center">URL</th>
                        <th class="text-center">Description</th>
                        <th class="text-center">User</th>
                        <th class="text-center">24x24</th>
                        <th class="text-center">48x48</th>
                        <th class="text-center">96x96</th>
                    </tr>
                </thead>
                <tbody>
                    {% for row in rows %}
                    <tr class="table align-middle">
                        <td class="text-center"><font color="#0D6EFD">{{ row.domain }}</font></td>
                        <td class="text-center">{{ row.name }}</td>
                        <td class="text-center">{{ row.url }}</td>
                        <td>{{ row.description }}</td>
                        <td class="text-center"><a class="btn btn-outline-primary btn-sm" role="button" href="{{ row.slug_link }}" target="_blank">{{ row.slug }}</a></td>
                        <td class="text-center">{{ '-' if row.avatar_urls_24 == '-' else '<img src="' + row.avatar_urls_24 + '" alt="Avatar">' }}</td>
                        <td class="text-center">{{ '-' if row.avatar_urls_48 == '-' else '<img src="' + row.avatar_urls_48 + '" alt="Avatar">' }}</td>
                        <td class="text-center">{{ '-' if row.avatar_urls_96 == '-' else '<img src="' + row.avatar_urls_96 + '" alt="Avatar">' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        <footer class="bd-footer text-bg-dark ">
        <div class="container py-3 py-md-3 px-3 px-md-3 text-body-secondary">
            <div class="row">
            <div class="col-lg-12 mb-12 text-center">
                <span><a class="btn btn-danger role="button" href="https://github.com/100security/wur" target="_blank">github.com/100security/wur</a></span>
            </div>

            </div>
        </div>
        </footer>
        </div><br>

    </body>
    </html>
    """

    template = Template(template_html)
    rendered_html = template.render(rows=df.to_dict(orient="records"), counts=counts_df.to_dict(orient="records"))
    
    # Saving the HTML file
    with open("reports/wur-report.html", "w") as f:
        f.write(rendered_html)

    clear_screen()

    yellow_color_code = "\033[33m"
    cyan_color_code = "\033[36m"
    green_color_code = "\033[92m"
    bold_code = '\033[1m'
    normal_code = '\033[22m'
    reset_color_code = "\033[0m"

    print(yellow_color_code + r"""
                                                                            
.  .   .  ..--.      .   .                      .--.                     .  
 \  \ /  / |   )     |   |                      |   )                   _|_ 
  \  \  /  |--'      |   |.--. .-. .--..--.     |--'  .-. .,-.  .-. .--. |  
   \/ \/   |         :   ;`--.(.-' |   `--.     |  \ (.-' |   )(   )|    |  
    ' '    '          `-' `--' `--''   `--'     '   ` `--'|`-'  `-' '    `-'
                                                          |                 
""" + reset_color_code)
    print(cyan_color_code + "By: Marcos Henrique | " + bold_code + "github.com/100security/wur" + normal_code + " | 100security.com.br/wur" + reset_color_code)
    print(cyan_color_code + "----------------------------------------------------------------------------" + reset_color_code + "\n")
    print(green_color_code + "Result: Report generated successfully!" + reset_color_code + "\n")

if __name__ == "__main__":
    main()
