# Challenge 4: Parking Lot System

An OOP-based parking lot management system with multiple floors and vehicle types.

## Features

- Multi-floor parking lot
- Three spot sizes: Small, Medium, Large
- Three vehicle types: Bike ($1/hr), Car ($2/hr), Truck ($3/hr)
- Park and unpark with ticket-based system
- Automatic fee calculation
- Status reporting

## Usage

```bash
python parking_lot.py
```

## Commands

```
park bike ABC123       # Park a bike with plate ABC123
park car XYZ789        # Park a car
park truck TRK456      # Park a truck
unpark 1               # Unpark vehicle with ticket ID 1
status                 # Show parking lot status
quit                   # Exit
```

## Example Session

```
> park car ABC123
Parked car ABC123
Ticket ID: 1
Spot: 11 (Floor 1)
Rate: $2.0/hr

> park bike XYZ789
Parked bike XYZ789
Ticket ID: 2
Spot: 1 (Floor 1)
Rate: $1.0/hr

> status
Parking Lot Status:
Floor 1: 2/25 occupied, 23 available
Floor 2: 0/25 occupied, 25 available

> unpark 1
Unparked vehicle
Fee: $2.50
```

## Design Patterns

- Factory Pattern: VehicleFactory creates vehicles
- Strategy Pattern: Each vehicle has its own pricing strategy
- Singleton Pattern: ParkingLot instance (optional)

## Spot Compatibility

- Bikes require Small spots (can use Medium or Large)
- Cars require Medium spots (can use Large)
- Trucks require Large spots

## Design Focus

- Clean class hierarchy
- Extensibility for new vehicle types
- Edge case handling (full lot, invalid ticket, wrong spot size)
- Proper encapsulation
