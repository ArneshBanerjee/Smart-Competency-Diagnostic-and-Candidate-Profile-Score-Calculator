from requests_html import HTMLSession
import csv


def job_data_get(s, url: str) -> tuple:
    # return the elements for each job card
    r = s.get(url)
    return r.html.find('ul.pagination-list a[aria-label=Next]'), r.html.find('div.job_seen_beacon')


def parse_html(job) -> dict:
    # Safely extract job details with error checks
    job_dict = {
        'title': job.find('h2 > a')[0].text if job.find('h2 > a') else 'No title',
        'link': 'https://in.indeed.com/viewjob?jk=' + job.find('h2 > a')[0].attrs['data-jk']
        if job.find('h2 > a') and 'data-jk' in job.find('h2 > a')[0].attrs else 'No link',
        'companyname': job.find('span.companyName')[0].text if job.find('span.companyName') else 'No company name',
        'snippet': job.find('div.job-snippet')[0].text.replace('\n', '').strip()
        if job.find('div.job-snippet') else 'No snippet'
    }

    # Check for the salary field
    try:
        job_dict['salary'] = job.find('div.metadata.salary-snippet-container')[0].text
    except IndexError:
        job_dict['salary'] = 'no salary info'

    return job_dict


def export(results):
    # Export results to CSV
    keys = results[0].keys() if results else []
    with open('results.csv', 'w') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)


def main():
    job_search = 'python'
    baseurl = 'https://in.indeed.com'
    

    s = HTMLSession()
    results = []
    url = baseurl + f'/jobs?q={job_search}&l=Bristol'
    r = s.get(baseurl)
    print(r.html.html)  # Print the HTML content to debug
    while True:
        jobs = job_data_get(s, url)
        for job in jobs[1]:
            results.append(parse_html(job))

        # Safely handle pagination
        try:
            if jobs[0]:  # Check if there's a next button
                url = baseurl + jobs[0][0].attrs['href']
                print(url)
            else:
                print("No more pages.")
                break
        except IndexError as err:
            print("Error finding next page:", err)
            break

    # Export the collected results
    if results:
        export(results)
    else:
        print("No results to export.")


if __name__ == '__main__':
    main()
