`mediastation-remote`
=====================

This Python scripts use [impacket](https://github.com/fortra/impacket/) to provide a CLI or REST service to shutdown or adjust the volume of a media station (which is just a Windows workstation). The benifit of this approach is taht it doesn't need any addtional software on the client and doesn't has any dependencies to a windows based host operating system for this component.

# Running

## REST Api

```
python app/api.py 
```

Afterwards you can see the doc in your browser at [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs)

## CLI Examples

Silence the remote machine:
```
python app/remote-admin.py -m 172.16.199.128 -u Test -p test volume --level 0
```

Shut down the remote machine:
```
python app/remote-admin.py 172.16.199.128 Test test shutdown 
```

For other possible options run:
```
python app/remote-admin.py --help
```

# Building a Docker image

```
docker build -t ghcr.io/cmahnke/mediastation-remote:latest .
```

## Running the Docker image

```
docker run -p 8000:80 ghcr.io/cmahnke/mediastation-remote:latest
```

You can open the docs in the browser with this URL: [http://localhost:8000/docs](http://localhost:8000/docs)

# Setting up the clients

Windows 11 and certainly earlier versions are far better secured then they used to be, so there are several configuration settings required:

## Security

* [Enable WMI Access (`winrm`)](https://stackoverflow.com/a/38905171)
* [Make sure that the network mode is not set to "public"](https://www.tenforums.com/tutorials/6815-set-network-location-private-public-domain-windows-10-a.html)

## Dependencies

For the volume control feature you need to have a recent [NuGet](https://www.nuget.org/) version:

```
Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force
```

# Status

* This is currently only tested against a Windows 11 VM, the domain mode still needs to be tested.
* A status check of a remote machine might be helpful as well
* A example for how to coonfigure Group policies for setting up the client settings (see above) should be provided