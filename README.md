This is the README for the GNPS2 Workflows deployment tooling. The goal of this repository is to be included in actual workflows so that we are able to deploy workflows one at a time. 

## Dependencies

```
fabric2
patchwork
pyyaml
```


## SSH Config

You need to update your ssh config file in the ~/home/.ssh/ folder to include the following:

```
Host ucr-gnps2
    Hostname gnps2.org
    User user
```
