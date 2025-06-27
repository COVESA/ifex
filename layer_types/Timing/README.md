# Layer Type: Timing v1.0

This Layer Type defines metadata that modifies the timing / rate of data exchange.  Data items themselves are defined as `Property` in the IFEX Core IDL.  The layer however also allows adding the same information to operations (`Method`s) and `Event`s.

## Rules, usage, and definition

The detailed description may refer to 'data' here, but it applies similarly to method calls and events.  Some of the possibilities, like a minimum rate for a method call, will probably not be used in _most_ systems.  It is rare, but possible, to require a method to be called with regular intervals.  
The target objects are Events, Methods and Properties. Both methods and events are actively "sent" (initiatiated) so applying a timing rate to them should be obvious.  Properties are not an action in themselves - they are only an abstraction of the underlying data item.  However, the assumption is that if timing constraints are applied to properties using this layer, then those will be used by environments that are exectuting some actions _related to_ the property.  Example: If a Pub/Sub semantics is applied then this is expected to limit the rate of update-signals, and if getter/setter polling style is applied then the timing constraints could be used to limit them.

If interpretation is unclear please remember that anything _not_ specified in the Layer Type definition (or cannot be reasonably inferred), is left open for further refinement -- typically expected to be described within the documentation of the tools that use the layer type.

### Tree-matching

This layer applies information to the objects defined in an IFEX Core model.  Therefore, to find and match the objects to modify, the tree structure of the layer mimics the IFEX Core AST.

Matching objects in the tree is done with these fields:

- name
- datatype (only for Property, not Method or Event!)

If both name and datatype are specified, then both must match for the object to be matched.  If either one is defined, only that one must match.  For example, constraints can be applied to all arguments of a certain datatype, without naming them.

Only the fields used for matching objects, and the new fields described below are allowed in the layer.
For example, a `description` field may not be specified, because the layer is not intended to modify description.

Wildcards are supported, for example '*' for name.
(TODO: refer to general description of how wildcard matching works)


### Rate limiting metadata

- Any field using the word 'frequency' is specified in Hz.  
  - Only whole integer numbers are allowed for frequency.  No unit shall be supplied.

- Any field using the word 'period':
  - Can be specified with a number followed by a time unit.  Allowed units are:  s, ms, us, ns, ps (meaning seconds, milli-, micro-, nano-, and pico-seconds respectively).  The unit suffix can follow the number without a space, or with maximum one space between.
  - Only whole integer numbers are allowed.  If a fraction is required, switch to a smaller unit instead.
  - If no suffix is specified, the number shall be interpreted as milliseconds.

### Simple period/frequency field:
 
- The simple fields `period` and `frequency` may be specified.  Depending on the code-generator details and the features of the final system, these metadata fields may be interpreted as specifying minimum, maximum, or both.  For example, one system might be involved in sending out data updates periodically and therefore interpret this as the desired (minimum) frequency, whereas another system is involved in controlling or checking the incoming rate of the same and interpret it as the maximum frequency instead.

- If `period` is specified then `min_period` and `max_period` may NOT be specified.  Analogous for frequency.

### Detailed period/frequency fields

- `min_period` and `max_period` is used to control systems that send updates regularly, or forward an incoming data. 

- min stands for minimum, max for maximum.

- For example, `max_period` (`max_frequency`) might be used to control a timer for cyclic signal or event that shall always be sent out with this rate. (See preferred_rate below, for a refined reasoning)

- This layer type does not specify more specific information such as error-margins, or maximum allowable jitter for the specified timings, and so on.  Alternative Layer Types could be defined where this is required.


### Typical usage

- `min_period` or `max_frequency` might be used to limit the forwarding rate through a software layer.  If incoming signals exceed this rate, the layer _might_ have the policy to drop the extra updates, to not forward them, or something else.  The layer type does not specify the exact behavior here - each tool, policy in the particular system, and the chosen code generation details would decide this.

- Period and Frequency fields that control the same aspect must not be defined at the same time, because of the risk of conflicting specification.  Even if the value matches (e.g. period 500 ms = frequency 2 Hz), it is not allowed to specify both.

### Extent of behavior definition 

The extent of the behavior definition in the Layer Type here is to a certain level of expectation.   Specific implementations need to interpret and document refined details if that is needed.

Consider, for example, there is no 'preferred_rate' metadata specified that can be added to min and max.  In such systems we may expect the simple `period` or `frequency` to be used.  If however, the layer instead specifies min/max, each tool, policy in the particular system, and the chosen code generation details would control the programed system behavior based on the input.  A system _might_ for example decide to set up a timer interrupt to exactly the max_period (and consequently ignore execution delays and jitter, because this is considered good enough in that particular system), _or_ it may choose to subtract a fixed number from the max_period to have a stronger behavioral guarantee.  In a system that would like to implement or track strict real-time behavior, it might choose the strategy to send signals using the middle between min and max periods (if both are defined), etc.  

The point is that the Layer Type does not specify behavior in more detail than is stated here.  Each tool and environment must refine and document further details, if that is required.

## Bugs

For this layer, object-matching using 'datatype' only makes sense for properties, not events or methods.  However, the schema does not strictly enforce that datatype field shall only be written on properties.  Presumably, this will not happen since there is no such field under the Method or Event type in the Core, but this is open for improvement in the schema.
