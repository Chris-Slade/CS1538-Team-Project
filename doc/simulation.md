# Customer Arrivals

At the beginning of the day, arrival times for customers are drawn from a
distribution and `Arrival` events are added to the event queue. When an
`Arrival` event is encountered in the event loop, the customer is added to the
seating queue. Customers wait here until a server is ready to seat them.

# Idle Servers

At the beginning of the day, `ServerIdle` events are added to the event
queue for each server there. (The number of servers is determined by the
`--num-servers` option, which defaults to 2.)

When a `ServerIdle` event is encountered in the event loop, the server looks at
the seating queue and the outgoing drink queue. The server's choice of which
queue to address is a function (which we'll have to decide) of the lengths of
the queues and the availability of seating at the bar.

## Seating Queue

If the server decides to address the seating queue, a customer will be removed
from the front of that queue and given a seat at the bar. Two new events will
then be pushed: an `OrderDrink` event for the customer, which decrements the
customer's desired drinks by one, and a new `ServerIdle` event for the server,
who will have finished seating the customer.

The times of these two new events will both be determined as an offset of the
original `ServerIdle`'s time and will follow some distribution. In other words,
after the server decides to seat a customer, the server will become idle and
the customer will become ready to place a drink order after some random period
of time.

## Incoming Order Queue

There are two instances in which `OrderDrink` events can occur. The first
is when a customer has just been seated (see [Seating Queue][]). The second
is when a customer has had an order delivered — if the customer still
desires more drinks, a new `OrderDrink` event will be placed when the customer
receives the drink, with its time being offset from the time the customer gets
the drink.

Pseudocode:

```
# Initialize state variables
seating_queue        ← new queue()
incoming_order_queue ← new queue()
outgoing_order_queue ← new queue()
events.push(customer_arrivals)

# Event loop
while event ← events.pop():
  switch typeof(event):

    case Arrival:
      seating_queue.push(arrival.get_customer())

    case ServerIdle:
      time        ← event.get_time()
      server      ← event.get_server()
      if handle_seating_queue():
        customer    ← seating_queue.pop()
        time_offset ← seating_time_offset()
        events.push(new OrderDrink(time=time + time_offset, customer=customer))
        events.push(new ServerIdle(time=time + time_offset, server=server))
      else:
        order       ← outgoing_order_queue.pop()
        customer    ← order.get_customer()
        time_offset ← drink_time_offset()
        events.push(DeliverDrink(time=time + time_offset, customer=customer))
        events.push(ServerIdle(time=time + time_offset, server=server))

    case OrderDrink:
      customer ← event.get_customer()
      order_queue.push(new DrinkOrder(type=random_type(), customer=customer))
```

# Bartenders

Bartenders can become idle like servers. Unlike servers, bartenders only have
one action to perform: preparing drinks.

Pseudocode:

```
# Inside event loop
case BartenderIdle:
  if incoming_order_queue is not empty:
    bartender ← event.get_bartender()
    order     ← incoming_order_queue.pop()
    customer  ← order.customer
    prep_time ← order.drink_type.prep_time()
    events.push(PreppedDrink(time=time + prep_time, order=order)
    events.push(BartenderIdle(time=time + prep_time, bartender=bartender)
  else:
    events.push(BartenderIdle(time=event.get_time() + 30))
```
