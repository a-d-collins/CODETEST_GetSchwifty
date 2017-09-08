from httplib import *

def deliver_packages():
    """
    Steps:
    1) Get time it takes for all drones to return to the warehouse.
    2) Sort drones by time to arrival.
    3) Get time to destination for all packages from warehouse.
    4) Sort packages by difference between time available to send package and time from warehouse to destination.
    5) If we want to get a package to its destination the soonest:
        a) assign (if possible) the first drone to the first package
        b) take the drone and package off of the lists/queues and
        c) add drone/package pair to "assignements" list.
        - If not possible to deliver package, put package in "unassigned" list.
    6) If, instead, we want to maximize the number of packages delivered, we can do one of at least two things:
        a) Pick lowest ranked drone that can possibly deliver a package, do this for all packages until we have the maximum
        number of drones/packages in the "assignments" list, THEN try to optimize delivery times without sacrificing the
        number of deliveries. This optimizing can be accomplished by swapping drones or checking if another drone can get
        a given package to its destination faster.

        b) Find all possible arrangements of drones to packages and see which ones deliver the most packages and then which
        of those arrangements minimizes delivery time.
    :return:
    """
    drones, packages = update_drones_and_packages(get_drones(), get_packages())
    return optimal_drone_delivery(drones, packages)


def update_drones_and_packages(drones, packages):
    # get time it takes for all drones to return to the warehouse
    drones = update_drone_data(drones)

    # sort drones by time it takes to get to warehouse
    # TODO

    # update packages with time it takes for them to get to their destinations
    packages = update_package_data(packages)

    # sort packages by total time available - time to destination from warehouse
    # TODO

    return [drones, packages]


def optimal_drone_delivery(drones, packages):
    return {}


def get_drones():
    return get_data_from_api("codetest.kube.getswift.co", "GET", "/drones")


def get_packages():
    return get_data_from_api("codetest.kube.getswift.co", "GET", "/packages")


def get_data_from_api(host, method, url):
    conn = HTTPConnection(host)
    conn.request(method, url)
    response = conn.getresponse()
    if response.status == 200:
        data = response.read()
        conn.close()
    else:
        data = []

    return data


def update_drone_data(drones):
    pass


def update_package_data(packages):
    pass
