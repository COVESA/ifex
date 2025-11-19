# Layer Types / AccessControl v0.9 (WIP)

This Layer Type defines metadata that can manage and enforce access control
policies on exchanged data. It can define access rules for all interface
features that define an active behavior, such as Method, Event, or Property.

Like all IFEX descriptions, it is an abstract description of the generally
expected behavior, which shall be translated into concrete enforcement when
implemented in a target environment, for example through code generation.

## Rules, usage, and definition

### Tree-matching

This layer applies information to the objects defined in an IFEX Core model. Therefore, to find and match the objects to modify, the tree structure of the layer mimics the IFEX Core AST.

The target objects are Properties, Methods and Events.

Matching objects in the tree is done with these fields:

- name

Only the fields used for matching objects, and the new fields described below are allowed in the layer. For example, a "description" field may not be specified, because the layer is not intended to modify description.

Wildcards are supported, for example '*' for name.
(TODO: refer to general description of how wildcard matching works)

 Either include a dedicated subsection explaining the specific wildcard syntax and behavior (e.g., * for zero or more characters, ? for a single character, similar to common ACL wildcard masks) or provide a clear reference to an existing IFEX general description.


### Access Control Definitions

#### Client Profiles

A combination of Role-Based Access control (RBAC) and direct identities in an access control list, should be supported by this abstraction.

What is not possible to express with this layer type is a complex Attribute-Based Access Control (Type Enforcement), similar to SELinux.  An alternative layer type could be defined if something at that level is required.

Access control rules are defined using client-profiles.  A 'client-profile' is a collective term for both client identifiers and/or roles.  The generally expected behavior is that a client identifiers represent the unique identity of a client (an application, another software component, etc.) that attempts to access the resource.  It is also generally expected that a client can belong to multiple roles.

For the value part of the `access:`, `read:` or `write:` fields, it is possible to list one or many client-profiles for each permission. Use the standard YAML syntax for a single values or a list.

Wildcards can be used to pattern-match on the object name, and be specified for the client-profiles to match multiple roles.  To use wildcard matching on the client-profiles likely requires the system to know the whole set of roles, which is client-profiles.

The access control rules define in an abstract way, the ability to access properties or methods, and to take part in events.  The target environment, together with the `action` field, decides what shall happen if an attempt is made without the right credentials.  Most usage of IFEX is within systems with explicitly pre-defined interfaces, so it is a rare situation, but the target environment and tools could also determine whether the _existence_ of a non-accessible object shall even be known to the client.


#### Hierarchical policy and client exclusion

Unless specified, each permission is an Allow-List with the default policy is to block access unless expressly allowed.  It is however possible for any environment to *expressly* document if the default behavior shall be allow, but in this case it must also verify and document the behavior clearly. The description that follows in later paragraphs has only been evaluated to be sound and unambiguous if following the deny-by-default principle.

Access control rules specified at one level of the hierarchy are inherited by all children, recursively.

To refine the rules a minus sign prefix before a client-profile at a lower level indicates exclusion from the inherited list.  This mechanism allows for exceptions to broader rules, enabling precise control over permissions.

The Union principle is followed so that access is granted if a client possesses _any_ of the specified client-profiles at any level, *unless explicitly excluded*.  Exclusions take precedence over inclusions, meaning if a client-profile is both included and excluded at different levels, the exclusion rule applies.  If visibility rules are applied in a particular environment then similarly nodes are visible to clients possessing any of the client-profiles specified at any level, unless explicitly excluded.


#### Properties
- The `access` field specifies permissions for `read` and `write` operations.  Each operation can list a set of client-profiles that are allowed to access the data for reading or writing.
- Example:
  ```yaml
  namespace:
    interface:
      properties:
        - name: Sys_Mgr_State
          access:
            read:
              - client1
              - coordinator_*   # Wildcard : all known profiles whose name starts with "coordinator_"
            write: state_writer
  ```

**Comment**: For data, it would be possible to define a concept covering HTTP or database-like behavior, where 'documents' or more generally data items are expected to be defined at run-time, and defining access control individually for the CRUD (Create, Read, Update, Delete) operations.  However, IFEX core IDL is most likely used for interfaces, where properties are predefined.  A later layer proposal may still explore a CRUD based access control if a useful concept can be found.  In the simple case, a program that allows dynamic creation and deletion of 'properties' would use the available features and define explicit methods call to handle this, and explaining the behavior accordingly.

#### Methods
    - The `access` field directly specifies the client-profile that can access (call) the method.
    - Example:
      ```yaml
      namespaces:
        - name: ns1
          interface:
            methods:
              - name: initialize
                access: client_role_1
              - name: shutdown
                access:
                - app_this_that
                - app_another
      ```

#### Events

Events are defined as a non-returning information outreach that may be sent by a software component, acting as a method-call that carries information but does not expect a reply.  (Refer to the IFEX specification for a clearer description).

Events have a single field named `access`, just like methods.  The intention is that clients that have access would receive the event when it is fired, and those that do not have access would not not.  This isn't possible to control in all systems - it will depend a lot on the target environment.  If the target environment only treats events as pure "broadcasts" which cannot be limited to particular receivers, then access control on events might not be feasible.  The implementations of tools and code generators for each target environment is expected to give appropriate feedback if the request described in the input file (the layer) can't be fulfilled in this target environment.

If the system either implements unicast events that have a dedicated receiver, or other mechanisms to control access to events (e.g. a client can request them), then this should be limited by the access-control rules.

Finally (and this applies to all features), if a system implements some kind of service-discovery mechanism that will also describe an interface at run-time, then it is customary to adjust the answer so it does not make clients aware of the existence of Events/Methods/Properties that they do not have access to.

### Example Usage

- **Namespace Level**: Specifies client-profile A.
- **Interface Level**: Specifies `-client-profile A` and adds client-profile B.
- **Method Level**: Specifies client-profile C.
- **Result**:
  - A client with client-profile B can access the interface and all parts within it, but a client with client-profile A cannot.
  - A client with client-profile C can access the method, irrespective of if it also has client-profile B, or A.

### Action

`action` means the action to take if an access violation occurs. It can be set to one of the values defined below.

If an access attempt violates the defined policies, then the stated action would be initiated. For data (`Property`), this action might be taken in an implementation that manages access control.

Note: Every system is slightly different, and particular environments and code-generation tools too. Therefore the behavior descriptions here are general. As usual, a particular tool implementation can (and ought to) provide additional documentation that refines the description of what actually happens in a particular environment or implementation.

#### Action values for access violations

- `none` (or not defined) -- Deny access but take no additional action, with the exception of any standard behavior that is built into a particular target environment or system (such as returning an error from the method).
- `pass` -- *Allow* the access despite a violation - typically for temporary use or in combination with another action like "log".  Instead of over-using pass, in a final system version the access control rules should be set up to explicitly allow access if possible.
.  Not so useful but can be specified temporarily during development
- `log` -- Use the system's logging feature to note the access violation.
- `alert` -- Use some predefined notification function to alert another part of the system about the access violation.
- `custom` -- Other action not covered by previous definitions.  For these cases, it is likely that a variation of the layer is created to add another value to specify the exact action, but if for some reason that isn't done then `custom` can be used.

Single value and list-value examples:
```yaml
  access: Privilege_Level_1
  action:
    - pass
    - log
  ...
  access:
    - Applications
    - Logger_Role
```

If no action is defined, it is assumed to be `none`.

### Combined Example

```yaml
namespace:
  access:
    - Applications
  interface:
    methods:
      - name: if1
        access:
          - -Media_App  # (minus-sign) = remove Media_App access even if it is part of Applications role
          - +client-profile D  # (Plus-sign is optional)
    properties:
      - name: Sys_State
        access:
          read:
            - App2
          write:
            - App2
            - App3
          action:  log
```
