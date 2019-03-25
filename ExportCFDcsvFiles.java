package macro;

import java.util.*;

import star.common.*;
import star.base.neo.*;

public class ExportCFDcsvFiles extends StarMacro {

	public void execute() {
		execute0();
	}

	private void execute0() {
		Simulation simulation_0 = getActiveSimulation();


		// probably should put this in a loop, but don't feel like figure out loops in java right now, so just copy and paste it all for now.

		// can't figure out how to get starccm+ to accept a variable on the command line or figure out what it's current simulation name is,
		// so just export to static filenames and then immediately rename with the calling python script after this script exits.

		XyzInternalTable xyzInternalTable_0 = ((XyzInternalTable) simulation_0.getTableManager().getTable("bottom half channel"));
		xyzInternalTable_0.extract();
		xyzInternalTable_0.export(resolvePath("exported_data/BottomHalfChannel.csv"), ",");

		XyzInternalTable xyzInternalTable_1 = ((XyzInternalTable) simulation_0.getTableManager().getTable("bottom wall"));
		xyzInternalTable_1.extract();
		xyzInternalTable_1.export(resolvePath("exported_data/BottomWall.csv"), ",");

		XyzInternalTable xyzInternalTable_2 = ((XyzInternalTable) simulation_0.getTableManager().getTable("top half channel"));
		xyzInternalTable_2.extract();
		xyzInternalTable_2.export(resolvePath("exported_data/TopHalfChannel.csv"), ",");

		XyzInternalTable xyzInternalTable_3 = ((XyzInternalTable) simulation_0.getTableManager().getTable("top wall"));
		xyzInternalTable_3.extract();
		xyzInternalTable_3.export(resolvePath("exported_data/TopWall.csv"), ",");


	}
}


