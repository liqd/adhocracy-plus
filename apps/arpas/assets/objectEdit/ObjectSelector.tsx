import React from "react";
import { Plus, X } from "lucide-react";
import { OBJECTS, useDraftStorage } from "../storage";
import ObjectDemo from "./ObjectDemo";

function ObjectSelector() {
    const { draft, setDraft } = useDraftStorage();
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <>
            {draft.placeObjectUrl ? (
                <button
                    className="btn"
                    style={{ zIndex: 9999 }}
                    onClick={() => {
                        setDraft({
                            ...draft,
                            placeObjectUrl: undefined,
                        });
                    }}
                >
                    <X size={24} />
                </button>
            ) : (
                <></>
                // <Drawer open={isOpen} onOpenChange={setIsOpen}>
                //   <DrawerTrigger asChild>
                //     <Button className="fixed bottom-4 right-4" style={{ zIndex: 9999 }}>
                //       <Plus size={24} />
                //     </Button>
                //   </DrawerTrigger>

                //   <DrawerContent>
                //     <DrawerHeader>
                //       <DrawerTitle>Objekt hinzufügen</DrawerTitle>
                //     </DrawerHeader>

                //     <div className="grid grid-cols-3 gap-3 mb-12">
                //       {OBJECTS.map((object, index) => (
                //         <button
                //           key={index}
                //           className="cursor-pointer w-full h-32"
                //           onClick={() => {
                //             setDraft({
                //               ...draft,
                //               placeObjectUrl: object.url,
                //             });
                //             setIsOpen(false);
                //           }}
                //         >
                //           <ObjectDemo url={object.url} />
                //         </button>
                //       ))}
                //     </div>
                //   </DrawerContent>
                // </Drawer>
            )}
        </>
    );
}

export default ObjectSelector;
