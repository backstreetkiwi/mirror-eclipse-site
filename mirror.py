from subprocess import Popen, PIPE, STDOUT
import sys

def execute(command, directory='.', verbose=False):
	p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, cwd=directory, close_fds=True)
	for c in iter(lambda: p.stdout.read(1), ''):
		if verbose:
			sys.stdout.write(c)
	rc = p.poll()
	if(rc and rc!=0):
		sys.exit(rc)


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
									<url>%(url)s</url>
									<layout>p2</layout>
								</repository>
							</source>
							<destination>${project.build.directory}/mirror/</destination>

							<ius>
								<iu>
									<id>net.sourceforge.pmd.eclipse.feature.group</id>
									<version>4.0.8.v20151204-2156</version>
								</iu>
							</ius>

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

execute("rm -rf mirror-eclipse-site/")

execute("mkdir mirror-eclipse-site")

data = {'name':'pmd', 'url':'https://dl.bintray.com/pmd/pmd-eclipse-plugin/updates/'}

with open("mirror-eclipse-site/pom.xml", "w") as pomFile:
	pomFile.write(pomXml%data)
	
with open("mirror-eclipse-site/assembly.xml", "w") as pomFile:
	pomFile.write(assemblyXml)
	
execute("cd mirror-eclipse-site")

execute("mvn package", "mirror-eclipse-site", verbose=True)

execute("cp mirror-eclipse-site/target/mirror-eclipse-site-1.0-mirror.zip %(name)s.zip"%data)

execute("rm -rf mirror-eclipse-site/")
