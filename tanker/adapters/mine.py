from adapter import Solver, dist, route_load
import time


# =========================================================
# 1. 2-OPT
# =========================================================

def two_opt(instance, route):

    if len(route) < 3:
        return False

    improved = False

    while True:

        changed = False

        n = len(route)

        for i in range(n - 1):

            a = 0 if i == 0 else route[i - 1]
            b = route[i]

            for j in range(i + 1, n):

                c = route[j]
                d = 0 if j == n - 1 else route[j + 1]

                old_distance = (
                    dist(instance, a, b)
                    + dist(instance, c, d)
                )

                new_distance = (
                    dist(instance, a, c)
                    + dist(instance, b, d)
                )

                if new_distance < old_distance:

                    route[i:j + 1] = reversed(
                        route[i:j + 1]
                    )

                    changed = True
                    improved = True
                    break

            if changed:
                break

        if not changed:
            break

    return improved


# =========================================================
# 2. INITIAL SOLUTION
# =========================================================

def create_initial_routes(instance):

    villages = list(
        range(1, instance.size + 1)
    )

    # Put villages having larger demand first.
    villages.sort(
        key=lambda v: instance.demand[v],
        reverse=True
    )

    routes = []
    loads = []

    for village in villages:

        demand = instance.demand[village]

        placed = False

        # Try putting the village into an existing route.
        for i in range(len(routes)):

            if (
                loads[i] + demand
                <= instance.capacity
            ):

                routes[i].append(village)

                loads[i] += demand

                placed = True

                break

        # If it doesn't fit anywhere,
        # create a new tanker route.
        if not placed:

            if len(routes) >= instance.fleet:

                return None

            routes.append([village])

            loads.append(demand)

    return routes


# =========================================================
# 3. IMPROVE BY MOVING ONE VILLAGE
# =========================================================

def best_relocation(instance, routes):

    best_change = 0

    best_move = None

    loads = [
        route_load(instance, route)
        for route in routes
    ]

    for r1 in range(len(routes)):

        route1 = routes[r1]

        # Don't completely remove a route.
        if len(route1) <= 1:
            continue

        for i in range(len(route1)):

            village = route1[i]

            demand = instance.demand[village]

            previous1 = (
                0
                if i == 0
                else route1[i - 1]
            )

            next1 = (
                0
                if i == len(route1) - 1
                else route1[i + 1]
            )

            # Distance removed from route 1.
            old_part_1 = (
                dist(instance, previous1, village)
                + dist(instance, village, next1)
            )

            new_part_1 = dist(
                instance,
                previous1,
                next1
            )

            change1 = new_part_1 - old_part_1

            # Try every other route.
            for r2 in range(len(routes)):

                if r1 == r2:
                    continue

                # Capacity check.
                if (
                    loads[r2] + demand
                    > instance.capacity
                ):
                    continue

                route2 = routes[r2]

                # Try every insertion position.
                for position in range(
                    len(route2) + 1
                ):

                    previous2 = (
                        0
                        if position == 0
                        else route2[position - 1]
                    )

                    next2 = (
                        0
                        if position == len(route2)
                        else route2[position]
                    )

                    old_part_2 = dist(
                        instance,
                        previous2,
                        next2
                    )

                    new_part_2 = (
                        dist(
                            instance,
                            previous2,
                            village
                        )
                        +
                        dist(
                            instance,
                            village,
                            next2
                        )
                    )

                    change2 = (
                        new_part_2
                        - old_part_2
                    )

                    total_change = (
                        change1 + change2
                    )

                    if total_change < best_change:

                        best_change = total_change

                        best_move = (
                            r1,
                            i,
                            r2,
                            position
                        )

    if best_move is None:
        return False

    r1, i, r2, position = best_move

    village = routes[r1].pop(i)

    routes[r2].insert(
        position,
        village
    )

    return True


# =========================================================
# 4. IMPROVE BY SWAPPING TWO VILLAGES
# =========================================================

def best_swap(instance, routes):

    best_change = 0

    best_move = None

    loads = [
        route_load(instance, route)
        for route in routes
    ]

    for r1 in range(len(routes)):

        for r2 in range(r1 + 1, len(routes)):

            route1 = routes[r1]
            route2 = routes[r2]

            for i in range(len(route1)):

                village1 = route1[i]

                for j in range(len(route2)):

                    village2 = route2[j]

                    # Check capacity after swap.
                    new_load1 = (
                        loads[r1]
                        - instance.demand[village1]
                        + instance.demand[village2]
                    )

                    new_load2 = (
                        loads[r2]
                        - instance.demand[village2]
                        + instance.demand[village1]
                    )

                    if new_load1 > instance.capacity:
                        continue

                    if new_load2 > instance.capacity:
                        continue

                    # -------- Route 1 --------

                    previous1 = (
                        0
                        if i == 0
                        else route1[i - 1]
                    )

                    next1 = (
                        0
                        if i == len(route1) - 1
                        else route1[i + 1]
                    )

                    old1 = (
                        dist(
                            instance,
                            previous1,
                            village1
                        )
                        +
                        dist(
                            instance,
                            village1,
                            next1
                        )
                    )

                    new1 = (
                        dist(
                            instance,
                            previous1,
                            village2
                        )
                        +
                        dist(
                            instance,
                            village2,
                            next1
                        )
                    )

                    # -------- Route 2 --------

                    previous2 = (
                        0
                        if j == 0
                        else route2[j - 1]
                    )

                    next2 = (
                        0
                        if j == len(route2) - 1
                        else route2[j + 1]
                    )

                    old2 = (
                        dist(
                            instance,
                            previous2,
                            village2
                        )
                        +
                        dist(
                            instance,
                            village2,
                            next2
                        )
                    )

                    new2 = (
                        dist(
                            instance,
                            previous2,
                            village1
                        )
                        +
                        dist(
                            instance,
                            village1,
                            next2
                        )
                    )

                    total_change = (
                        new1
                        + new2
                        - old1
                        - old2
                    )

                    if total_change < best_change:

                        best_change = total_change

                        best_move = (
                            r1,
                            i,
                            r2,
                            j
                        )

    if best_move is None:
        return False

    r1, i, r2, j = best_move

    routes[r1][i], routes[r2][j] = (
        routes[r2][j],
        routes[r1][i]
    )

    return True


# =========================================================
# 5. IMPROVE ALL ROUTES USING 2-OPT
# =========================================================

def improve_all_routes(instance, routes):

    for route in routes:

        two_opt(
            instance,
            route
        )


# =========================================================
# 6. MAIN SOLVER
# =========================================================

class MySolver(Solver):

    def solve(
        self,
        instance,
        submit_candidate
    ):

        # ---------------------------------------------
        # STEP 1: Create an initial valid solution
        # ---------------------------------------------

        routes = create_initial_routes(
            instance
        )

        # If no valid solution could be constructed.
        if routes is None:

            return {
                "routes": []
            }

        # ---------------------------------------------
        # STEP 2: Improve route order
        # ---------------------------------------------

        improve_all_routes(
            instance,
            routes
        )

        # ---------------------------------------------
        # STEP 3: Submit first solution
        # ---------------------------------------------

        receipt = submit_candidate({
            "routes": routes
        })

        # ---------------------------------------------
        # STEP 4: Keep improving while time remains
        # ---------------------------------------------

        while receipt["remaining_s"] > 0.40:

            # Try moving one village.
            moved = best_relocation(
                instance,
                routes
            )

            if moved:

                improve_all_routes(
                    instance,
                    routes
                )

                receipt = submit_candidate({
                    "routes": routes
                })

                continue

            # If moving didn't help,
            # try swapping two villages.
            swapped = best_swap(
                instance,
                routes
            )

            if swapped:

                improve_all_routes(
                    instance,
                    routes
                )

                receipt = submit_candidate({
                    "routes": routes
                })

                continue

            break

        routes = [
            route
            for route in routes
            if len(route) > 0
        ]

    

        return {
            "routes": routes
        }