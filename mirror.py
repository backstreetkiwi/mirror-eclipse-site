from subprocess import Popen, PIPE, STDOUT
import sys

pomXml = """
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>

	<groupId>de.zaunkoenigweg.eclipse</groupId>
	<artifactId>mirror-eclipse-site</artifactId>
	<version>1.0</version>
	<packaging>pom</packaging>

	<properties>
		<tycho.version>1.0.0</tycho.version>
	</properties>

	<repositories>
		<repository>
			<id>oxygen</id>
			<url>http://download.eclipse.org/releases/oxygen</url>
			<layout>p2</layout>
		</repository>

	</repositories>

	<build>
		<plugins>
			<plugin>
				<groupId>org.eclipse.tycho.extras</groupId>
				<artifactId>tycho-p2-extras-plugin</artifactId>
				<version>${tycho.version}</version>
				<executions>
					<execution>
						<id>mirror</id>
						<phase>prepare-package</phase>
						<goals>
							<goal>mirror</goal>
						</goals>
						<configuration>
							<source>
								<repository>
									<url>%(siteUrl)s</url>
									<layout>p2</layout>
								</repository>
							</source>
							<destination>${project.build.directory}/mirror/</destination>
							<ius>
%(iuConfiguration)s							</ius>
						</configuration>
					</execution>
				</executions>
			</plugin>
			<plugin>
				<artifactId>maven-assembly-plugin</artifactId>
				<version>2.4.1</version>
				<configuration>
					<descriptors>
						<descriptor>assembly.xml</descriptor>
					</descriptors>
				</configuration>
				<executions>
					<execution>
						<phase>package</phase>
						<goals>
							<goal>single</goal>
						</goals>
					</execution>
				</executions>
			</plugin>
		</plugins>
	</build>
</project>
"""

assemblyXml="""<assembly xmlns="http://maven.apache.org/plugins/maven-assembly-plugin/assembly/1.1.2" 
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/plugins/maven-assembly-plugin/assembly/1.1.2 http://maven.apache.org/xsd/assembly-1.1.2.xsd">
  <id>mirror</id>
  <formats>
    <format>zip</format>
  </formats>
  <includeBaseDirectory>false</includeBaseDirectory>
  <fileSets>
    <fileSet>
      <directory>${project.build.directory}/mirror</directory>
      <outputDirectory>/</outputDirectory>
    </fileSet>
  </fileSets>
</assembly>"""

iusXml = """								<iu>
									<id>%(iu)s</id>
									<version>%(version)s</version>
								</iu>
"""


def execute(command, directory='.', verbose=False):
	p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=directory, close_fds=True)
	for c in iter(lambda: p.stdout.read(1), ''):
		if verbose:
			sys.stdout.write(c)
	rc = p.poll()
	if(rc and rc!=0):
		sys.exit(rc)


def prompt(msg, allowEmpty=False):
	text = raw_input(msg)
	if(not allowEmpty):
		while(not text.strip()):
			text = raw_input(msg)
	return text.strip()


print """

This mirroring tool helps you generating a zipped update site from a given site URL.
It dynamically creates a Maven project and uses a tycho plugin to mirror the update site.

You have to provide some params."""

print """

Site Name:
==========

The site name is used as the name for the zip file that contains the mirrored update site.

Example: "pmd"
"""

siteName = prompt("site name: ")

print """

update site URL:
================

The URL of the update site. You usually obtain it from the plugin's website.

Example: "https://dl.bintray.com/pmd/pmd-eclipse-plugin/updates/"
"""

siteUrl = prompt("update site URL: ")

print """

IUs (installable units):
========================

An update site can consist of multiple installable units (usually Eclipse features).
You can provide 0..n IU names. If you provide none, all available IUs will be mirrored,
otherwise the given subset.

Example: "net.sourceforge.pmd.eclipse.feature.group"
"""


ius = []
iu = prompt("IU # 1 (blank for all IUs): ", allowEmpty=True)
while(iu.strip()):
	ius.append(iu)
	iu = prompt("IU # %d (blank to end list): " % (len(ius)+1), allowEmpty=True)

versions = {}

for iu in ius:
	version = prompt("Version for IU '%s' (blank for latest): " % iu, allowEmpty=True)
	versions[iu]=version

print """


The script will now generate a Maven project in the subfolder mirror-eclipse-site
and execute it to mirror and assemble the site.


"""

raw_input("ENTER")

iuConfiguration = ""

for iu in ius:
	iuConfiguration += (iusXml % {'iu':iu, 'version': versions[iu]})

execute("rm -rf mirror-eclipse-site/")

execute("mkdir mirror-eclipse-site")

data = {'siteName':siteName, 'siteUrl':siteUrl, 'iuConfiguration':iuConfiguration}

with open("mirror-eclipse-site/pom.xml", "w") as pomFile:
	pomFile.write(pomXml % data)
	
with open("mirror-eclipse-site/assembly.xml", "w") as pomFile:
	pomFile.write(assemblyXml)

execute("cd mirror-eclipse-site")

execute("mvn package", "mirror-eclipse-site", verbose=True)

execute("cp mirror-eclipse-site/target/mirror-eclipse-site-1.0-mirror.zip %s.zip" % siteName)

execute("rm -rf mirror-eclipse-site/")

print """


If the Maven project was completed successfully, you find the update site in %s.zip.


""" % siteName

