# Overview

The zip file contains all the information necessary to fabricate the 5X ReSkin circuit board. The BOM, Bill of Materials, details the components needed to populate the corresponding circuit design. You may choose to manufacture by yourself, if you have access to a PCB mill, and solder yourself, with a reflow oven. However, we recommend ordering your boards from a 3rd party vendor, such as PCBWay or OSHPark, as they are relatively inexpensive, quick, and high-quality. 

  ### Note: The shipping is often the biggest bottleneck in price and time - consider placing large, shared orders if you are able.

  ### Note: The main magnetometer chip, MLX90393, is currently very low-stock. This is out of our control, but we hope it is resolved soon. We recommend purchasing from reputable distributers such as Digikey or Mouser.

# Ordering circuit boards from PCBWay (One Example)

1. Navigate to [PCBWay](https://www.pcbway.com/) and select ["PCB Instant Quote"](https://www.pcbway.com/orderonline.aspx) from the main menu bar.
2. The default option is to start a rigid boards. Select [FPC/Rigid Flex](https://www.pcbway.com/flexible.aspx) to start a flexible PCB order.
3. For rigid boards, select [quick-order PCB](https://www.pcbway.com/QuickOrderOnline.aspx) and upload the zip file here to "+Add Gerber File".
4. RIGID BOARDS ONLY: The board size will be automatically detected as 20x29mm. We recommend the below settings for the board, in sequential line-by-line order. The bold bullet points are different from the default options.
    - Board type: Single Pieces
    - Different Design in Panel: 1
    - Size: (auto-populated) 20x29mm
    - **Quantity: [your choice]**
    - Layers: 2 Layers
    - Material: FR-4
    - FR4-TG: TG130-140
    - **Thickness: 0.6**
    - Min Track/Spacing: 6/6mil
    - Min Hole Size: 0.3mm
    - Solder Mask: Green
    - Silkscreen: White
    - Edge Connector: No
    - Surface Finish: HASL with Lead or **Immersion gold (ENIG)**
    - Via Process: Tenting Vias
    - Finished Copper: 1oz Cu
    - Extra pcb product number: [your choice] Note: It is a 3$ fee to avoid PCBWay extra text over the design. Purely aesthetic, no functional difference.
    - Additional options: None
5. FLEX BOARDS ONLY: There is no option for quick upload. They will prompt for the zip file after adding to cart for approval. The bold bullet points are different from the default options.
    - PCB Type: Flexible PCB
    - Different Design in Panel: 1
    - **Layers: 2 Layers**
    - Board type: Single Pieces
    - Size: 20x29mm
    - **Quantity: [your choice]**
    - Polyimide base material: Polyimide Flex
    - FPC Thickness: 0.1
    - Min Track/Spacing: 0.06mm
    - Min Hole size/pad size: 0.15/0.35mm
    - Solder Mask: Yellow Coverlay or **Black Coverlay**
    - Silkscreen: White or **Black**
    - Edge Connector: No
    - Stiffener: without
    - Surface Finish: Immersion Gold (ENIG)
    - Thickness of Immersion Gold: 1U"
    - Finished Copper: 1 oz Cu (35um)
    - E-test: 100%
    - 3M/Tesa tape: without
    - EMI shielding film: without
    - Other Special Request: None
6. Assembly service
    - Turnkey 
    - Board type: single pieces
    - Quantity: [number of boards you want assembled, can be equal to or less than number of boards manufactured above]
    - Pay attention: No sensitive parts
    - Number of unique parts: 6
    - Number of SMD parts: 6
    - Number of BGA/QFP parts: 0
    - Number of through-hole parts: 0
    - Detailed information of assembly: If you request assembly at the same time as boards, you may leave this empty. If you first requested boards, and assembly later on, put the Product No of the boards that you can find under "Under Review".

Add the boards and assembly services to cart. It will usually be approved within 24 hours. After approval, you may add the items to cart and pay following their instructions.
