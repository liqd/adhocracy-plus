import React, { createContext, use, useContext, useState } from "react";
import { Euler, Vector3 } from "three";

export const OBJECTS = [
    {
        name: "Baum",
        url: "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/tree-spruce/model.gltf",
    },
    {
        name: "Bank",
        url: "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/bench-2/model.gltf",
    },
    {
        name: "Laterne",
        url: "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/lamp-post/model.gltf",
    },
];

export const OBJECT_SCALES: {
    [key: string]: number;
} = {
    "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/tree-spruce/model.gltf": 0.1,
    "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/bench-2/model.gltf": 1,
    "https://vazxmixjsiawhamofees.supabase.co/storage/v1/object/public/models/lamp-post/model.gltf": 1,
};

type Object = {
    url: string;
    position: Vector3;
    scale: Vector3;
    rotation: Euler;
};

type Draft = {
    objects: Object[];

    placeObjectUrl?: string;
};

const DEFAULT_DRAFT: Draft = {
    objects: [],
};

export const draftStorageContext = createContext<{
    draft: Draft;
    setDraft: (draft: Draft) => void;
}>({
    draft: DEFAULT_DRAFT,
    setDraft: () => {},
});

export function DraftStorageProvider({
    children,
}: {
    children: React.ReactNode;
}) {
    const [draft, setDraft] = useState<Draft>(DEFAULT_DRAFT);

    return (
        <draftStorageContext.Provider
            value={{
                draft,
                setDraft,
            }}
        >
            {children}
        </draftStorageContext.Provider>
    );
}

export function useDraftStorage() {
    return useContext(draftStorageContext);
}
