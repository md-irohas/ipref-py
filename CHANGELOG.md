# ChangeLog

## v0.3.0 / 2023-08-23

- [WEB] Add API (v1) to look-up IP addresses.


## v0.2.1 / 2023-05-01

- [CLI/WEB] Fix a bug that tildes in filenames are not expanded.


## v0.2.0 / 2023-01-18

- [CLI/WEB] Add an option to specify nameservers' IP addresses for DNS lookups.
    - config.yaml.orig: dns.reverse_name.nameservers
- [CLI/WEB] Add version number to config.yaml.orig.
- [WEB] The nameservers are shown in the web interface.
- [WEB] Add an option to show national flags after country codes.
    - config.yaml.orig: web.search[{name: Misc}]


## v0.1.0 / 2023-01-12

- [CLI] Support TSV for output_format.
- [WEB] Implement a simple web interface.
- [CLI/WEB] Send DNS queries only when they are needed.


## v0.0.0

This is the first commit.
This commit includes rough implementation to look up IP addresses in GeoIP
databases by a command.
