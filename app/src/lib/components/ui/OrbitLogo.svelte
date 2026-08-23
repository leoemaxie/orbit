<script lang="ts">
	interface Props {
		size?: 'sm' | 'md' | 'lg';
		showWordmark?: boolean;
		animated?: boolean;
		class?: string;
	}

	let {
		size = 'md',
		showWordmark = true,
		animated = true,
		class: className = ''
	}: Props = $props();

	const iconSizes = {
		sm: 'w-7 h-7',
		md: 'w-9 h-9',
		lg: 'w-12 h-12'
	};

	const wordmarkSizes = {
		sm: 'text-sm tracking-wide',
		md: 'text-base tracking-widest',
		lg: 'text-xl tracking-[0.2em]'
	};
</script>

<div class="inline-flex items-center gap-2.5 select-none {className}">
	<!-- Vector Planetary Orbit Mark -->
	<div class="relative {iconSizes[size]} shrink-0 flex items-center justify-center">
		<!-- Outer Diffuse Glow -->
		{#if animated}
			<div class="absolute -inset-1 bg-orbit-cyan/20 rounded-full blur-sm animate-pulse-slow"></div>
		{/if}

		<svg
			viewBox="0 0 100 100"
			class="w-full h-full relative z-10 overflow-visible"
			fill="none"
			xmlns="http://www.w3.org/2000/svg"
		>
			<defs>
				<linearGradient id="orb-grad-{size}" x1="0%" y1="0%" x2="100%" y2="100%">
					<stop offset="0%" stop-color="#00F2FE" />
					<stop offset="50%" stop-color="#38BDF8" />
					<stop offset="100%" stop-color="#3B82F6" />
				</linearGradient>

				<linearGradient id="ring-grad-{size}" x1="0%" y1="0%" x2="100%" y2="100%">
					<stop offset="0%" stop-color="#00F2FE" />
					<stop offset="60%" stop-color="#8B5CF6" />
					<stop offset="100%" stop-color="#38BDF8" />
				</linearGradient>

				<filter id="core-glow-{size}" x="-20%" y="-20%" width="140%" height="140%">
					<feGaussianBlur stdDeviation="2" result="blur" />
					<feMerge>
						<feMergeNode in="blur" />
						<feMergeNode in="SourceGraphic" />
					</feMerge>
				</filter>
			</defs>

			<!-- Orbit Ring 1 (Tilted -26deg) -->
			<g transform="translate(50,50) rotate(-26)">
				<ellipse
					cx="0"
					cy="0"
					rx="42"
					ry="15"
					stroke="url(#ring-grad-{size})"
					stroke-width="2.5"
					stroke-dasharray="4 2"
					class={animated ? 'animate-[spin_16s_linear_infinite]' : ''}
					style="transform-origin: center;"
				/>
				<!-- Beacon Probe on Orbit 1 -->
				<circle cx="39" cy="-5" r="4.5" fill="#00F2FE" filter="url(#core-glow-{size})" />
				<circle cx="39" cy="-5" r="2" fill="#FFFFFF" />
			</g>

			<!-- Orbit Ring 2 (Tilted +35deg) -->
			<g transform="translate(50,50) rotate(35)">
				<ellipse
					cx="0"
					cy="0"
					rx="38"
					ry="13"
					stroke="#8B5CF6"
					stroke-width="2"
					opacity="0.75"
				/>
				<!-- Satellite node on Orbit 2 -->
				<circle cx="-35" cy="4" r="3.5" fill="#8B5CF6" />
				<circle cx="-35" cy="4" r="1.5" fill="#FFFFFF" />
			</g>

			<!-- Central Planetary Data Core -->
			<circle cx="50" cy="50" r="15" fill="url(#orb-grad-{size})" filter="url(#core-glow-{size})" />
			<circle cx="50" cy="50" r="9.5" fill="#07090E" opacity="0.4" />
			<circle cx="50" cy="50" r="4.5" fill="#FFFFFF" />
		</svg>
	</div>

	<!-- Optional Wordmark & Telemetry Badge -->
	{#if showWordmark}
		<div class="flex flex-col">
			<div class="flex items-center gap-1.5 leading-none">
				<span class="font-extrabold text-white font-sans {wordmarkSizes[size]}">
					ORBIT
				</span>
				<span class="w-1.5 h-1.5 rounded-full bg-orbit-emerald animate-pulse"></span>
			</div>
			<span class="text-[9px] font-mono font-semibold tracking-wider text-orbit-cyan-glow uppercase mt-0.5 opacity-90">
				Autonomous Data Ops
			</span>
		</div>
	{/if}
</div>
