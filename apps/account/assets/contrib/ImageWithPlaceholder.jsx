import React from 'react'

const ImageWithPlaceholder = ({ src, alt, lazy = true, ...rest }) => {
  const hasImage = src && src.length
  return hasImage
    ? (
      <img
        src={src}
        alt={alt}
        loading={lazy ? 'lazy' : 'eager'}
        {...rest}
      />
      )
    : (
      <picture>
        <source type="image/webp" srcSet="/static/images/placeholder_tile.webp" />
        <source type="image/avif" srcSet="/static/images/placeholder_tile.avif" />
        <img
          src="/static/images/placeholder_tile.svg"
          alt={alt}
          loading={lazy ? 'lazy' : 'eager'}
          {...rest}
        />
      </picture>
      )
}

export default ImageWithPlaceholder
