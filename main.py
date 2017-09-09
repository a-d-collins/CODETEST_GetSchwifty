from httplib import *
from geopy.distance import vincenty
import copy
import datetime

from utils.bisect_helpers import BisectHelpers


WAREHOUSE_LAT = -37.816359
WAREHOUSE_LNG = 144.963848
DRONE_SPEED = 50 # km / h
START_TIME = datetime.datetime.now()


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
        c) add drone/package pair to "assignments" list.
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
    drones = sorted(drones, key=lambda x: x["hours_to_warehouse"])

    # update packages with time it takes for them to get to their destinations
    packages = update_package_data(packages)
    # sort packages by total time available - time to destination from warehouse
    packages = sorted(packages, key=lambda x: x["dest_hours_from_warehouse"])

    return [drones, packages]


def optimal_drone_delivery(drones, packages):
    bisect_helpers = BisectHelpers()

    result = {
        "assignments": [],
        "unassignedPackageIds": []
    }

    tmp_drones = copy.deepcopy(drones)
    used_drones = []
    for package in packages:
        # Find rightmost index of drone that can deliver the package
        # This drone represents the drone that can just barely get the package to its destination on time
        deadline = datetime.datetime.fromtimestamp(package["deadline"])
        datetime_diff = deadline - datetime.timedelta(hours=package["dest_hours_from_warehouse"]) - START_TIME
        hour_limit = datetime_diff.total_seconds() / 3600
        idx = bisect_helpers.find_lt_by_key(tmp_drones, hour_limit, "hours_to_warehouse")

        if idx is None:
            result["unassignedPackageIds"].append(package["packageId"])
        else:
            result["assignments"].append({"droneId": tmp_drones[idx]["droneId"], "packageId": package["packageId"]})
            used_drones.append(tmp_drones[idx])
            tmp_drones.pop(idx)

    # TODO: replace drones with ones that are faster

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
    for drone in drones:
        if len(drone["packages"]) > 0:
            drone_dist_to_warehouse = vincenty(
                (drone["location"]["latitude"], drone["location"]["longitude"]),
                (drone["packages"][0]["destination"]["latitude"], drone["packages"][0]["destination"]["longitude"])
            ).kilometers

            drone_dist_to_warehouse += vincenty(
                (drone["packages"][0]["destination"]["latitude"], drone["packages"][0]["destination"]["longitude"]),
                (WAREHOUSE_LAT, WAREHOUSE_LNG)
            ).kilometers
        else:
            drone_dist_to_warehouse = vincenty(
                (drone["location"]["latitude"], drone["location"]["longitude"]),
                (WAREHOUSE_LAT, WAREHOUSE_LNG)
            ).kilometers

        drone["hours_to_warehouse"] = drone_dist_to_warehouse / DRONE_SPEED


def update_package_data(packages):
    for package in packages:
        dest_dist_from_warehouse = vincenty(
            (WAREHOUSE_LAT, WAREHOUSE_LNG),
            (package["destination"]["latitude"], package["destination"]["longitude"])
        ).kilometers
        package["dest_hours_from_warehouse"] = dest_dist_from_warehouse / DRONE_SPEED
