<template>
  <div ref="mapContainer" class="w-full h-[600px]"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import * as d3 from 'd3'
import { feature } from 'topojson-client'
import { useSolarStore } from '../stores/solar'
import type { SolarState } from '../types'

const mapContainer = ref<HTMLElement | null>(null)
const solarStore = useSolarStore()

const emit = defineEmits<{
  (e: 'stateSelected', state: SolarState): void
}>()

onMounted(async () => {
  if (!mapContainer.value) return

  try {
    // Fetch US map data
    const usResponse = await fetch('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json')
    const us = await usResponse.json()

    // Use store data
    const solarData = solarStore.solarData

    // Set up the map
    const width = mapContainer.value.clientWidth
    const height = 600
    
    // Create SVG
    const svg = d3.select(mapContainer.value)
      .append('svg')
      .attr('width', width)
      .attr('height', height)

    // Create projection
    const projection = d3.geoAlbersUsa()
      .fitSize([width, height], feature(us, us.objects.states))

    // Create path generator
    const path = d3.geoPath().projection(projection)

    // Create color scale
    const colorScale = d3.scaleSequential(d3.interpolateBlues)
      .domain([0, d3.max(solarData, d => d.total_capacity_ac) || 0])

    // Create states
    svg.selectAll('path')
      .data(feature(us, us.objects.states).features)
      .enter()
      .append('path')
      .attr('d', path)
      .attr('fill', (d: any) => {
        const stateData = solarData.find(s => s.state === d.properties.name)
        return stateData ? colorScale(stateData.total_capacity_ac) : '#eee'
      })
      .attr('stroke', 'white')
      .attr('stroke-width', 0.5)
      .on('mouseover', function() {
        d3.select(this).attr('stroke-width', 2)
      })
      .on('mouseout', function() {
        d3.select(this).attr('stroke-width', 0.5)
      })
      .on('click', (event, d: any) => {
        const stateData = solarData.find(s => s.state === d.properties.name)
        if (stateData) {
          emit('stateSelected', stateData)
        }
      })

    // Add legend
    createLegend(svg, colorScale, height)

  } catch (error) {
    console.error('Error creating map:', error)
  }
})

const createLegend = (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, 
                     colorScale: d3.ScaleSequential<string, never>, 
                     height: number) => {
  const legend = svg.append('g')
    .attr('transform', `translate(20, ${height - 60})`)

  const legendWidth = 200
  const legendHeight = 10

  const legendScale = d3.scaleLinear()
    .domain(colorScale.domain())
    .range([0, legendWidth])

  const legendAxis = d3.axisBottom(legendScale)
    .ticks(5)
    .tickFormat(d => `${d3.format('.0f')(Number(d))} MW`)

  legend.append('g')
    .call(legendAxis)
    .attr('transform', `translate(0, ${legendHeight})`)

  const defs = svg.append('defs')
  const linearGradient = defs.append('linearGradient')
    .attr('id', 'legend-gradient')
    .attr('x1', '0%')
    .attr('y1', '0%')
    .attr('x2', '100%')
    .attr('y2', '0%')

  linearGradient.selectAll('stop')
    .data(colorScale.ticks().map((t, i, n) => ({ 
      offset: `${i * 100 / (n.length - 1)}%`,
      color: colorScale(t) 
    })))
    .enter()
    .append('stop')
    .attr('offset', d => d.offset)
    .attr('stop-color', d => d.color)

  legend.append('rect')
    .attr('width', legendWidth)
    .attr('height', legendHeight)
    .style('fill', 'url(#legend-gradient)')
}
</script>