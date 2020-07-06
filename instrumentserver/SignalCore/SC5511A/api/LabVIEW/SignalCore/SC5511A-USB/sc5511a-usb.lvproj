<?xml version='1.0' encoding='UTF-8'?>
<Project Type="Project" LVVersion="10008000">
	<Item Name="My Computer" Type="My Computer">
		<Property Name="NI.SortType" Type="Int">3</Property>
		<Property Name="server.app.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.control.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="server.tcp.enabled" Type="Bool">false</Property>
		<Property Name="server.tcp.port" Type="Int">0</Property>
		<Property Name="server.tcp.serviceName" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.tcp.serviceName.default" Type="Str">My Computer/VI Server</Property>
		<Property Name="server.vi.callsEnabled" Type="Bool">true</Property>
		<Property Name="server.vi.propertiesEnabled" Type="Bool">true</Property>
		<Property Name="specify.custom.address" Type="Bool">false</Property>
		<Item Name="SC5511A-USB" Type="Folder" URL="..">
			<Property Name="NI.DISK" Type="Bool">true</Property>
		</Item>
		<Item Name="Dependencies" Type="Dependencies">
			<Item Name="vi.lib" Type="Folder">
				<Item Name="Error Cluster From Error Code.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Error Cluster From Error Code.vi"/>
				<Item Name="whitespace.ctl" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/whitespace.ctl"/>
				<Item Name="Trim Whitespace.vi" Type="VI" URL="/&lt;vilib&gt;/Utility/error.llb/Trim Whitespace.vi"/>
				<Item Name="subTimeDelay.vi" Type="VI" URL="/&lt;vilib&gt;/express/express execution control/TimeDelayBlock.llb/subTimeDelay.vi"/>
			</Item>
			<Item Name="sc5511a.dll" Type="Document" URL="sc5511a.dll">
				<Property Name="NI.PreserveRelativePath" Type="Bool">true</Property>
			</Item>
		</Item>
		<Item Name="Build Specifications" Type="Build">
			<Item Name="SC5511A_SoftFrontPanel" Type="EXE">
				<Property Name="App_copyErrors" Type="Bool">true</Property>
				<Property Name="App_INI_aliasGUID" Type="Str">{B64FFE85-6F32-46E9-ABF9-00307F4F5F03}</Property>
				<Property Name="App_INI_GUID" Type="Str">{FB4EEC3A-9EA0-42FF-B6BA-BBE725687752}</Property>
				<Property Name="Bld_buildSpecName" Type="Str">SC5511A_SoftFrontPanel</Property>
				<Property Name="Bld_excludeLibraryItems" Type="Bool">true</Property>
				<Property Name="Bld_excludePolymorphicVIs" Type="Bool">true</Property>
				<Property Name="Bld_localDestDir" Type="Path">/I/projects/falcon/sc5511a/development/software/api/rev2.0/usb/libusb/labview/builds/SC5511A_SoftFrontPanel</Property>
				<Property Name="Bld_modifyLibraryFile" Type="Bool">true</Property>
				<Property Name="Destination[0].destName" Type="Str">SC5511A_SoftFrontPanel.exe</Property>
				<Property Name="Destination[0].path" Type="Path">/I/projects/falcon/sc5511a/development/software/api/rev2.0/usb/libusb/labview/builds/SC5511A_SoftFrontPanel/SC5511A_SoftFrontPanel.exe</Property>
				<Property Name="Destination[0].path.type" Type="Str">&lt;none&gt;</Property>
				<Property Name="Destination[0].preserveHierarchy" Type="Bool">true</Property>
				<Property Name="Destination[0].type" Type="Str">App</Property>
				<Property Name="Destination[1].destName" Type="Str">Support Directory</Property>
				<Property Name="Destination[1].path" Type="Path">/I/projects/falcon/sc5511a/development/software/api/rev2.0/usb/libusb/labview/builds/SC5511A_SoftFrontPanel/data</Property>
				<Property Name="Destination[1].path.type" Type="Str">&lt;none&gt;</Property>
				<Property Name="DestinationCount" Type="Int">2</Property>
				<Property Name="Exe_iconItemID" Type="Ref">/My Computer/SC5511A-USB/application/sci.ico</Property>
				<Property Name="Source[0].itemID" Type="Str">{45CB2783-FFA0-465F-890A-34117E819D2F}</Property>
				<Property Name="Source[0].type" Type="Str">Container</Property>
				<Property Name="Source[1].destinationIndex" Type="Int">0</Property>
				<Property Name="Source[1].itemID" Type="Ref">/My Computer/SC5511A-USB/application/sc5511a_soft_front_panel.vi</Property>
				<Property Name="Source[1].sourceInclusion" Type="Str">TopLevel</Property>
				<Property Name="Source[1].type" Type="Str">VI</Property>
				<Property Name="SourceCount" Type="Int">2</Property>
				<Property Name="TgtF_companyName" Type="Str">SignalCore Inc.</Property>
				<Property Name="TgtF_fileDescription" Type="Str">SC5511A_SoftFrontPanel</Property>
				<Property Name="TgtF_fileVersion.major" Type="Int">1</Property>
				<Property Name="TgtF_fileVersion.minor" Type="Int">1</Property>
				<Property Name="TgtF_internalName" Type="Str">SC5511A_SoftFrontPanel</Property>
				<Property Name="TgtF_legalCopyright" Type="Str">Copyright © 2015 SignalCore Inc</Property>
				<Property Name="TgtF_productName" Type="Str">SC5511A_SoftFrontPanel</Property>
				<Property Name="TgtF_targetfileGUID" Type="Str">{2C0067DF-AAC1-4B24-8927-3D6378E5C7BD}</Property>
				<Property Name="TgtF_targetfileName" Type="Str">SC5511A_SoftFrontPanel.exe</Property>
			</Item>
		</Item>
	</Item>
</Project>
