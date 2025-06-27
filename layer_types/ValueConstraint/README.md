# Layer Types / ValueConstraint v1.0

This Layer Type defines metadata that can check or control constraints on exchanged values.  It is likely to be applied to `Property` definitions, but some features are applicable also on `Method` and `Event` parameters.

## Rules, usage, and definition

The detailed description will refer to 'data' here, but applies to properties as well as method and event parameters.

### Tree-matching

This layer applies information to the objects defined in an IFEX Core model.  Therefore, to find and match the objects to modify, the tree structure of the layer mimics the IFEX Core AST.

The target objects are Properties, parameters (Argument) within Methods (input, output and returns), and Arguments in Events (input).

Matching objects in the tree is done with these fields:

- name
- datatype

If both name and datatype are specified, then both must match for the object to be matched.  If either one is defined, only that one must match.  For example, constraints can be applied to all arguments of a certain datatype, without naming them.

Only the fields used for matching objects, and the new fields described below are allowed in the layer.
For example, a "description" field may not be specified, because the layer is not intended to modify description.

Wildcards are supported, for example '*' for name.
(TODO: refer to general description of how wildcard matching works)


### Value Constraints

- Upper Bound: `max_value`
- Lower Bound: `min_value`
- Delta Limit: `delta`, `delta_up` and `delta_down`.  This puts constraints on the maximum amount that a value can change compared to the previous value that was received for the same data item or parameter.  Delta can be specified using an absolute number, or by a number followed by a percent-sign (%) after the number.  
  - `delta` is the maximum change in either direction and shall be specified using a positive number.  Calculate the absolute value of the difference of the new value and the old value, and the constraint is that it shall be less than or equal to the stated delta.
  - `delta` specified in percentage (positive number) can be calculated with the following formula:  abs(100 * (new_value - old_value)/old_value).  If the absolute value of the percentage is greater than the specified delta, the new value is considered outside of the allowed constraint.
  - `delta_up` must be specified by a positive number and it only puts limits on the rate of increase.  The condition is: if (new_value - old_value > delta_up), then the value is outside the constraint.
  - `delta_up` specified as a percentage is a positive number followed by '%'.  Check if 100 * ((new_value - old_value) / abs(old_value)) is greater than the percentage.  (In cases that new_value is less than old_value the calculation becomes negative, which is not greater than the always-positive stated percentage.
  - `delta_down` shall be specified by a *negative* number and it only puts limits on the rate of decrease.  The condition is: if (new_value - old_value < delta_down), then the value is outside the constraint.  
  - `delta_down` specified as a percentage is a negative number followed by '%'.  Check if 100 * ((new_value - old_value) / abs(old_value)) is less than the (negative) percentage.  In cases that new_value is greater than old_value the calculation becomes positive, which is not less than the always-negative stated percentage.

### Action

`action` means the action to take if a value is outside of the constraints.  It can be set to one of the values defined below.

If an incoming value violates the defined constraints then the stated action would be initiated.  For data (`Property`), this action might be taken in an implementation that consumes incoming signals and forwards the original signal, or some derived calculation on a new channel.  For `Method` and `Event` parameters, the 'sender' naturally controls which value is sent, and could ensure that it is within bounds - so the defined action is expected to be taken on the side that receives the event or method call.

Note: Every system is slightly different, and particular environments and code-generation tools too.  Therefore the behavior descriptions here are general.  As usual, a particular tool implementation can (and ought to) provide additional documentation that refines the description of what actually happens in a particular environment or implementation.

#### Action values for 

- `none` (default) -- Take no action
- `clamp` -- Clamping means to limits the value to an upper or lower bound.  For example, if an incoming value is too small then it is treated as if it was equal to min_value.  Normal operation proceeds such as calculating a derived value, or forwarding the signal, using the min_value.  Analogous for values that are too large, which are then set to the max_value.
- `block` -- For an implementation involved in forwarding incoming data on a new channel, or sending out derived signals calculated from the input, or taking other action as a consequence of the incoming data - `block` shall prevent this if the incoming value is outside of the constraints.
- `log` -- Use the system's logging feature to note the value that was outside constraints
- `escalate` -- Use some predefined report function to notify another part of the system that an illegal value was noticed.
For example, this might notify health-monitor component.  The remedy or reaction to this is naturally system-specific.
- `custom` -- Other action not covered by previous definitions.  For these cases, it is likely that a variation of the layer is created to add another value to specify the exact action, but if for some reason that isn't done then `custom` can be used.

If no action is defined, it is assumed to be `none`

#### Action values for delta definitons

If a value is determined to be outside of constraints, then:

- `clamp` - Continue normal operation with the old_value plus the specified `delta_up` or `delta_down` respectively.  
 (Note: This adds a negative delta in the case of `delta_down`).   For the generic `delta`, proceed with (old_value + delta) if the new_value is greater than old_value, and proceed with (old_value - delta) if new_value was less than old_value.  For percentages, multiply old_value by (1 + 100 * percentage). 

- `ramp` - This is a more advanced operation that might not always be fitting the application.  If it is implemented, the system is expected to ramp towards the new_value, one delta at a time, until the new_value is reached.  How this works, such as how often to repeat an operation to achieve the "ramp", is usually tied to the use of a timing layer, or even more commonly implemented with the more advanced `delta_per_time` constraint.  Nonetheless, this layer allows for this action to be specified, and for specific implementations to interpret and further refine the behavior description.

- `none`, `block`, `log`, `escalate` and `custom` as described above.


### Value Over Time Constraints

These aspects specify expected or allowed rate of change, not compared to the previously received value, but measured over a particular time period.

In order to implement such constraints, the system needs to measure the time when the previous value was received, and calculate the delta divided by the time passed until the new value has been received.

`delta_per_time` with two associated metadata fields below it:  `value` and `time_period`.  Some implementations may support only a fixed value for time_period. 
`delta_up_per_time` -- same associated metadata.  Only affects increasing values.
`delta_down_per_time` -- same associated metadata.  Only affects decreasing values.

- `none`, `clamp`, `block`, `log`, `escalate` and `custom` behave analogously to previous definitions.

** Refer to Whitepaper **

