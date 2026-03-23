from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class SpotSize(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3


class VehicleType(Enum):
    BIKE = 1
    CAR = 2
    TRUCK = 3


class Vehicle(ABC):
    def __init__(self, license_plate):
        self.license_plate = license_plate
        self.vehicle_type = None

    @abstractmethod
    def get_required_spot_size(self):
        pass

    @abstractmethod
    def get_hourly_rate(self):
        pass


class Bike(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.BIKE

    def get_required_spot_size(self):
        return SpotSize.SMALL

    def get_hourly_rate(self):
        return 1.0


class Car(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.CAR

    def get_required_spot_size(self):
        return SpotSize.MEDIUM

    def get_hourly_rate(self):
        return 2.0


class Truck(Vehicle):
    def __init__(self, license_plate):
        super().__init__(license_plate)
        self.vehicle_type = VehicleType.TRUCK

    def get_required_spot_size(self):
        return SpotSize.LARGE

    def get_hourly_rate(self):
        return 3.0


class VehicleFactory:
    @staticmethod
    def create_vehicle(vehicle_type, license_plate):
        if vehicle_type == VehicleType.BIKE:
            return Bike(license_plate)
        elif vehicle_type == VehicleType.CAR:
            return Car(license_plate)
        elif vehicle_type == VehicleType.TRUCK:
            return Truck(license_plate)
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")


class ParkingSpot:
    def __init__(self, spot_id, size, floor):
        self.spot_id = spot_id
        self.size = size
        self.floor = floor
        self.vehicle = None
        self.is_occupied = False

    def can_fit(self, vehicle):
        required_size = vehicle.get_required_spot_size()
        return self.size.value >= required_size.value

    def park(self, vehicle):
        if self.is_occupied:
            raise ValueError(f"Spot {self.spot_id} is already occupied")
        if not self.can_fit(vehicle):
            raise ValueError(f"Vehicle does not fit in spot {self.spot_id}")

        self.vehicle = vehicle
        self.is_occupied = True

    def unpark(self):
        if not self.is_occupied:
            raise ValueError(f"Spot {self.spot_id} is empty")

        vehicle = self.vehicle
        self.vehicle = None
        self.is_occupied = False
        return vehicle


class Ticket:
    def __init__(self, ticket_id, vehicle, spot, entry_time):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.spot = spot
        self.entry_time = entry_time
        self.exit_time = None
        self.fee = 0.0

    def calculate_fee(self):
        if self.exit_time is None:
            self.exit_time = datetime.now()

        duration = (self.exit_time - self.entry_time).total_seconds() / 3600
        hourly_rate = self.vehicle.get_hourly_rate()
        self.fee = duration * hourly_rate
        return self.fee


class ParkingLot:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.spots = []
            cls._instance.tickets = {}
            cls._instance.ticket_counter = 0
        return cls._instance

    def add_floor(self, floor_num, small_spots, medium_spots, large_spots):
        spot_id = len(self.spots) + 1

        for _ in range(small_spots):
            self.spots.append(ParkingSpot(spot_id, SpotSize.SMALL, floor_num))
            spot_id += 1

        for _ in range(medium_spots):
            self.spots.append(ParkingSpot(spot_id, SpotSize.MEDIUM, floor_num))
            spot_id += 1

        for _ in range(large_spots):
            self.spots.append(ParkingSpot(spot_id, SpotSize.LARGE, floor_num))
            spot_id += 1

    def find_spot(self, vehicle):
        for spot in self.spots:
            if not spot.is_occupied and spot.can_fit(vehicle):
                return spot
        return None

    def park(self, vehicle):
        spot = self.find_spot(vehicle)
        if spot is None:
            raise ValueError(f"No available spot for vehicle {vehicle.license_plate}")

        spot.park(vehicle)

        self.ticket_counter += 1
        ticket = Ticket(self.ticket_counter, vehicle, spot, datetime.now())
        self.tickets[ticket.ticket_id] = ticket

        return ticket

    def unpark(self, ticket_id):
        if ticket_id not in self.tickets:
            raise ValueError(f"Invalid ticket ID: {ticket_id}")

        ticket = self.tickets[ticket_id]
        ticket.spot.unpark()

        fee = ticket.calculate_fee()
        del self.tickets[ticket_id]

        return fee

    def get_status(self):
        status = {}
        for spot in self.spots:
            floor = spot.floor
            if floor not in status:
                status[floor] = {'total': 0, 'occupied': 0, 'available': 0}

            status[floor]['total'] += 1
            if spot.is_occupied:
                status[floor]['occupied'] += 1
            else:
                status[floor]['available'] += 1

        return status


def main():
    lot = ParkingLot()

    lot.add_floor(1, small_spots=10, medium_spots=10, large_spots=5)
    lot.add_floor(2, small_spots=10, medium_spots=10, large_spots=5)

    print("Parking Lot System")
    print("Commands: park <type> <plate> | unpark <ticket_id> | status | quit")
    print("Types: bike, car, truck")

    while True:
        try:
            command = input("\n> ").strip()

            if not command:
                continue

            parts = command.split()
            action = parts[0].lower()

            if action == "quit" or action == "exit":
                break

            elif action == "park":
                if len(parts) < 3:
                    print("Error: Usage: park <type> <plate>")
                    continue

                vehicle_type_str = parts[1].lower()
                license_plate = parts[2]

                type_map = {
                    'bike': VehicleType.BIKE,
                    'car': VehicleType.CAR,
                    'truck': VehicleType.TRUCK
                }

                if vehicle_type_str not in type_map:
                    print(f"Error: Unknown vehicle type '{vehicle_type_str}'")
                    continue

                vehicle = VehicleFactory.create_vehicle(type_map[vehicle_type_str], license_plate)
                ticket = lot.park(vehicle)

                print(f"Parked {vehicle_type_str} {license_plate}")
                print(f"Ticket ID: {ticket.ticket_id}")
                print(f"Spot: {ticket.spot.spot_id} (Floor {ticket.spot.floor})")
                print(f"Rate: ${vehicle.get_hourly_rate()}/hr")

            elif action == "unpark":
                if len(parts) < 2:
                    print("Error: Usage: unpark <ticket_id>")
                    continue

                ticket_id = int(parts[1])
                fee = lot.unpark(ticket_id)

                print(f"Unparked vehicle")
                print(f"Fee: ${fee:.2f}")

            elif action == "status":
                status = lot.get_status()
                print("\nParking Lot Status:")
                for floor, data in sorted(status.items()):
                    print(f"Floor {floor}: {data['occupied']}/{data['total']} occupied, {data['available']} available")

            else:
                print(f"Unknown command: {action}")

        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
